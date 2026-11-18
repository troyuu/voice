"""Test Jamaica's registered tools through a fresh Codex app-server task (Python 3.11+)."""
import asyncio
import json
import secrets
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "plugins/jamaica-command-center/.codex/agents"


async def check(roles):
    proc = await asyncio.create_subprocess_exec(
        "codex", "app-server", "--listen", "stdio://", stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL, limit=8_000_000,
    )
    sequence = 0

    async def rpc(method, params):
        nonlocal sequence
        sequence += 1
        request = {"id": sequence, "method": method, "params": params}
        proc.stdin.write((json.dumps(request) + "\n").encode())
        await proc.stdin.drain()
        async with asyncio.timeout(90):
            while line := await proc.stdout.readline():
                msg = json.loads(line)
                if "method" in msg and "id" in msg:
                    raise RuntimeError(f"Codex requested interaction: {msg['method']}")
                if msg.get("id") == sequence:
                    if "error" in msg:
                        raise RuntimeError(msg["error"].get("message", method))
                    return msg["result"]
        raise RuntimeError("Codex closed the connection.")

    try:
        await rpc("initialize", {"clientInfo": {"name": "jamaica-check", "version": "1"},
                                 "capabilities": {"experimentalApi": True}})
        proc.stdin.write(b'{"method":"initialized"}\n')
        thread = await rpc("thread/start", {"cwd": str(ROOT), "ephemeral": True, "sandbox": "read-only"})
        endpoint = {"threadId": thread["thread"]["id"], "server": "jamaica-hermes"}
        pending = []
        for role in roles:
            result = await rpc("mcpServer/tool/call", {**endpoint, "tool": "hermes_status",
                                                       "arguments": {"role": role}})
            state = result.get("structuredContent") or json.loads(result["content"][0]["text"])
            if result.get("isError") or state.get("profile") != "jamaica-" + role or not state.get("reachable"):
                raise RuntimeError(f"Wrong or unavailable Hermes profile for {role}")
            token = "JAMAICA-" + secrets.token_hex(5)
            reply = await rpc("mcpServer/tool/call", {**endpoint, "tool": "hermes_consult",
                              "arguments": {"role": role, "question": f"Connection test. Please echo this exact receipt code: {token}"}})
            texts = [part.get("text", "").strip() for part in reply["content"]]
            if state["login_present"]:
                if reply.get("isError"):
                    raise RuntimeError(f"Hermes consultation failed for {role}: {texts[0][:240]}")
                if not any(token in text for text in texts):
                    raise RuntimeError(f"No matching model reply from {role}")
                print(f"{role}: verified model reply", flush=True)
            elif reply.get("isError") and any("Sign-in required" in s for s in texts):
                print(f"{role}: Hermes reached, sign-in required", flush=True)
                pending.append(role)
            else:
                raise RuntimeError(f"Unexpected unauthenticated response from {role}")
        return 2 if pending else 0
    finally:
        if proc.returncode is None:
            proc.terminate()
            await proc.wait()


if __name__ == "__main__":
    import argparse
    roles = ["command-center", *sorted(p.stem for p in AGENTS.glob("*.toml"))]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=roles, help="Check one role instead of the whole team.")
    selected = parser.parse_args().role
    sys.exit(asyncio.run(check([selected] if selected else roles)))
