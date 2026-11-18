# /// script
# requires-python = ">=3.11,<3.15"
# dependencies = ["mcp==1.30.0", "PyYAML==6.0.3"]
# ///
"""Set up Jamaica's private Hermes profiles and expose text consultations over stdio."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from typing import Literal, get_args

import yaml
from mcp.server.fastmcp import FastMCP

Role = Literal["command-center", "communications-specialist", "call-specialist",
               "operations-specialist", "research-specialist", "workflow-designer", "risk-reviewer"]
ROOT = Path.home() / ".local" / "share" / "jamaica-command-center"
PROFILES = ROOT / "hermes-home"
INSTALLED = ROOT / "bridge.py"
SERVER = "jamaica-hermes"
mcp = FastMCP(SERVER)


def profile(role):
    if role not in get_args(Role):
        raise ValueError("Unknown Jamaica role.")
    return "jamaica-" + role


def private_write(path, content):
    """Replace a managed file atomically, without exposing private profile data."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(content)
    os.replace(tmp.name, path)


def child_env():
    allowed = {"PATH", "HOME", "USER", "LOGNAME", "LANG", "TMPDIR", "TEMP", "TMP", "TERM",
               "SYSTEMROOT", "COMSPEC", "USERPROFILE", "LOCALAPPDATA", "APPDATA", "PATHEXT",
               "HOMEDRIVE", "HOMEPATH", "SSL_CERT_FILE", "HTTPS_PROXY", "NO_PROXY"}
    return {**{k: v for k, v in os.environ.items() if k.upper() in allowed},
            "HERMES_HOME": str(PROFILES), "NO_COLOR": "1", "PYTHONUTF8": "1"}


def hermes(role, *args, timeout=20, prompt=None):
    binary = (ROOT / "executable.txt").read_text().strip()
    return subprocess.run([binary, "-p", profile(role), *args], env=child_env(),
                          cwd=ROOT, input=prompt if prompt is not None else "",
                          capture_output=True, text=True, encoding="utf-8", errors="replace",
                          timeout=timeout)


@mcp.tool()
def hermes_status(role: Role) -> dict:
    """Ask the selected Hermes profile whether it has its own Codex sign-in."""
    name = profile(role)
    identity = hermes(role, "profile", "show", name)
    if identity.returncode or name not in identity.stdout:
        raise ValueError(f"Hermes could not open {name}. Run Jamaica's setup again.")
    auth = hermes(role, "auth", "list", "openai-codex")
    if auth.returncode:
        raise ValueError(f"Hermes could not inspect sign-in for {name}.")
    output = re.sub(r"\x1b\[[0-9;]*m", "", auth.stdout)
    return {"profile": name, "reachable": True,
            "login_present": bool(re.search(r"^openai-codex \([1-9]\d* credentials?\):\s*$",
                                            output, re.MULTILINE))}


@mcp.tool()
def hermes_consult(role: Role, question: str) -> str:
    """Ask one Jamaica specialist for text advice. Send only necessary, authorized context."""
    if not question.strip() or len(question) > 12000:
        raise ValueError("Supply a question between 1 and 12000 characters.")
    if not hermes_status(role)["login_present"]:
        raise ValueError(f"Sign-in required for {profile(role)}. Run the login step for {role}.")
    reply = hermes(role, "chat", "--oneshot", "--query-file", "-", "--format", "stream-json",
                   "--provider", "openai-codex", "--toolsets", "clarify", "--max-turns", "2",
                   "--source", "tool", timeout=50, prompt=question)
    for line in reversed(reply.stdout.splitlines()):
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if isinstance(record, dict) and record.get("type") == "result":
            if not reply.returncode and record.get("exit_code") == 0 and record.get("text"):
                return record["text"]
            break
    raise ValueError(f"{profile(role)} did not return a completed answer. Check its sign-in and model availability.")


def setup():
    package = Path(__file__).resolve().parents[2]
    agents = package / ".codex" / "agents"
    if not agents.is_dir():
        raise SystemExit("Run setup from the extracted Jamaica Command Center package.")
    binary, uv, codex = (shutil.which(cmd) for cmd in ("hermes", "uv", "codex"))
    if not all((binary, uv, codex)):
        raise SystemExit("Setup needs Hermes Agent, uv, and Codex CLI on this computer.")
    ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    subprocess.run([binary, "--version"], env=child_env(), cwd=ROOT, check=True, timeout=25)
    codex_agents = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "agents"
    config = {"model": {"provider": "openai-codex", "default": "gpt-6-astra"},
              "auth": {"adopt_external_logins": False}, "fallback_providers": [],
              "platform_toolsets": {"cli": ["clarify"]}, "mcp_servers": {},
              "memory": {"memory_enabled": False, "user_profile_enabled": False},
              "auxiliary": {"title_generation": {"enabled": False}}}
    for role in get_args(Role):
        if role == "command-center":
            continue
        target = codex_agents / ("jamaica-" + role + ".toml")
        if target.exists() and target.read_bytes() != (agents / (role + ".toml")).read_bytes():
            raise SystemExit(f"Review the existing specialist before replacing it: {target}")
    # Do not replace a different server that happens to use our name.
    launch = ["run", "--offline", "--script", str(INSTALLED), "serve"]
    existing = subprocess.run([codex, "mcp", "get", SERVER, "--json"], capture_output=True, text=True)
    if existing.returncode == 0:
        transport = json.loads(existing.stdout)["transport"]
        if transport.get("args") != launch or transport.get("command") != uv:
            raise SystemExit("Another jamaica-hermes server is configured. Review it before continuing.")
    encoded = (json.dumps(config, indent=2) + "\n").encode()
    private_write(ROOT / "executable.txt", binary.encode())
    for directory in [PROFILES] + [PROFILES / "profiles" / profile(r) for r in get_args(Role)]:
        cfg = directory / "config.yaml"
        if not cfg.exists():
            private_write(cfg, encoded)
        else:
            current = yaml.safe_load(cfg.read_text()) or {}
            if current.get("auth", {}).get("adopt_external_logins") is not False:
                raise SystemExit(f"Review sign-in isolation in {cfg} before continuing.")
    for role in get_args(Role):
        if role == "command-center":
            instructions = "Help Jamaica plan and review office work. Return advice to the main assistant."
        else:
            definition = (agents / (role + ".toml")).read_bytes()
            instructions = tomllib.loads(definition.decode())["developer_instructions"].split("Hermes consultation")[0].strip()
            private_write(codex_agents / ("jamaica-" + role + ".toml"), definition)
        soul = PROFILES / "profiles" / profile(role) / "SOUL.md"
        if not soul.exists():
            private_write(soul, (instructions + "\nGive text advice only. The main assistant handles actions and approvals.\n").encode())
    private_write(INSTALLED, Path(__file__).read_bytes())
    subprocess.run([uv, "run", "--offline", "--script", str(INSTALLED), "--help"],
                   stdout=subprocess.DEVNULL, check=True)
    if existing.returncode:
        subprocess.run([codex, "mcp", "add", SERVER, "--", uv, *launch], check=True)
    print("Seven private Hermes profiles and six Codex specialists are configured. Start a fresh Codex task.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["setup", "serve", "status", "login", "test"])
    parser.add_argument("role", nargs="?", choices=[*get_args(Role), "all"], default="all")
    args = parser.parse_args()
    if args.action == "setup":
        return setup()
    if args.action == "serve":
        return mcp.run(transport="stdio")
    roles = get_args(Role) if args.role == "all" else [args.role]
    for role in roles:
        state = hermes_status(role)
        if args.action == "login" and not state["login_present"]:
            print(f"Sign in for {state['profile']}. Choose a fresh OAuth sign-in.", flush=True)
            subprocess.run([(ROOT / "executable.txt").read_text().strip(), "-p", profile(role),
                            "auth", "add", "openai-codex", "--type", "oauth"], env=child_env(),
                           cwd=ROOT, check=True)
            state = hermes_status(role)
            if not state["login_present"]:
                raise SystemExit(f"{state['profile']} still needs sign-in.")
        if args.action == "test":
            import secrets
            token = secrets.token_hex(5)
            response = hermes_consult(role, f"Reply with exactly JAMAICA-{token} and nothing else.")
            if response.strip() != f"JAMAICA-{token}":
                raise SystemExit(f"No matching reply from {profile(role)}.")
            print(f"{profile(role)} returned the challenge.")
        else:
            print(json.dumps(state))


if __name__ == "__main__":
    main()
