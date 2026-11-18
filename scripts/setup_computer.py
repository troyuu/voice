"""Install an extracted release folder locally. Use 'login' and 'verify' to finish onboarding."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.request import urlopen


REPO = Path(__file__).resolve().parents[1]
NAME = "jamaica-command-center"
MARKET = "jamaica-tools"
PACKAGE = REPO / "plugins" / NAME
BRIDGE = PACKAGE / "integrations/hermes/bridge.py"
VERSION = "0.3.1"
PIN = "bf0203a794a07aac3ff764972ab9087baa4e4f4e"
HERMES_HOME = Path.home() / ".local/share" / NAME / "hermes-home"


def command(name):
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"{name} is missing from PATH. Follow SETUP.md on this computer and resume.")
    return path


def run(*args, capture=False):
    result = subprocess.run(args, cwd=REPO, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return json.loads(result.stdout) if capture else None


def ensure_hermes():
    if shutil.which("hermes"):
        return
    # A new user shell may not have picked up an existing install yet.
    windows = os.name == "nt"
    local_bin = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "hermes/bin" if windows else Path.home() / ".local/bin"
    engine = HERMES_HOME / "hermes-agent"
    os.environ["PATH"] += os.pathsep + os.pathsep.join(map(str, (local_bin, HERMES_HOME / "bin", engine / ".hermes/bin")))
    if shutil.which("hermes"):
        return
    prior = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "hermes" if windows else Path.home() / ".hermes"
    if (prior / "hermes-agent").exists() or (prior / "bin").exists():
        raise SystemExit("An existing Hermes install needs its launcher restored to PATH. See SETUP.md.")
    ext, checksum = (("ps1", "8d491a8b9b19934bb8d027b11962c394551798e969d244b68d4ab95295b970e2")
                     if windows else ("sh", "99cb3691d55019c6973a7acb775a915648666cc24e483ca827a1cdbb3531a674"))
    url = f"https://raw.githubusercontent.com/NousResearch/hermes-agent/{PIN}/scripts/install.{ext}"
    with tempfile.TemporaryDirectory() as tmp:
        installer = Path(tmp) / f"install.{ext}"
        with urlopen(url, timeout=30) as response:
            body = response.read()
        if hashlib.sha256(body).hexdigest() != checksum:
            raise SystemExit("The Hermes installer checksum does not match this release.")
        installer.write_bytes(body)
        HERMES_HOME.mkdir(mode=0o700, parents=True, exist_ok=True)
        # A new runtime may populate config.yaml on first launch. Set its
        # sign-in policy first, preserving any existing user-owned config.
        config = HERMES_HOME / "config.yaml"
        try:
            with config.open("x", encoding="utf-8") as out:
                out.write('{"auth":{"adopt_external_logins":false},"fallback_providers":[]}\n')
        except FileExistsError:
            pass
        if windows:
            run(command("powershell"), "-NoProfile", "-File", str(installer), "-Commit", PIN,
                "-HermesHome", str(HERMES_HOME), "-InstallDir", str(engine), "-NonInteractive")
        else:
            run(command("bash"), str(installer), "--commit", PIN, "--hermes-home", str(HERMES_HOME),
                "--dir", str(engine), "--non-interactive")
    # Hermes also publishes a launcher inside its checkout.
    command("hermes")


def check_plugin(codex):
    rows = run(codex, "plugin", "list", "--marketplace", MARKET, "--json", capture=True)["installed"]
    if not any(r["pluginId"] == f"{NAME}@{MARKET}" and r["version"] == VERSION and
               r.get("installed") and r.get("enabled") for r in rows):
        raise SystemExit(f"Jamaica Command Center {VERSION} must be installed and enabled before verification.")


def install_plugin(codex):
    stores = run(codex, "plugin", "marketplace", "list", "--json", capture=True)["marketplaces"]
    store = next((item for item in stores if item["name"] == MARKET), None)
    if store is None or Path(store["root"]).resolve() == REPO:
        run(codex, "plugin", "marketplace", "add", str(REPO))
    else:
        source = store.get("marketplaceSource", {})
        if source.get("sourceType") != "git" or source.get("source", "").removesuffix(".git") != "https://github.com/troyuu/voice":
            raise SystemExit("Jamaica Tools already points to another folder. Use its verified release checkout or review the source with Jamaica.")
        if not (REPO / ".git").exists():
            raise SystemExit("The existing marketplace uses GitHub. Keep it unchanged and ask Jamaica before switching it to the supplied local folder.")
        run(codex, "plugin", "marketplace", "upgrade", MARKET)
        manifest = Path(store["root"]) / "plugins" / NAME / ".codex-plugin/plugin.json"
        if json.loads(manifest.read_text())["version"] != VERSION:
            raise SystemExit("The existing Git marketplace resolves to a different version. Check its configured release.")
    installed = run(codex, "plugin", "add", f"{NAME}@{MARKET}", "--json", capture=True)
    cache = Path(installed["installedPath"])
    skill_paths = {f.relative_to(PACKAGE) for f in (PACKAGE / "skills").glob("*/SKILL.md")}
    helper_files = {Path("skills/learn-workflows/scripts/track_workflow.py"),
                    Path("skills/learn-workflows/scripts/helper_agent.py"),
                    Path("integrations/hermes/check_connection.py")}
    if installed.get("version") != VERSION or len(skill_paths) != 7 or any(
        not (cache / p).is_file() or (cache / p).read_bytes() != (PACKAGE / p).read_bytes() for p in skill_paths | helper_files
    ):
        raise SystemExit("The installed skills or helper files differ from this release.")
    check_plugin(codex)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=["install", "login", "verify"], nargs="?", default="install")
    step = parser.parse_args().step
    codex, uv = command("codex"), command("uv")
    if step == "install":
        run(sys.executable, str(REPO / "scripts/validate_pack.py"))
        ensure_hermes()
        install_plugin(codex)
        run(uv, "run", "--script", str(BRIDGE), "setup")
        print("Installed. Continue with the login step in Jamaica's own terminal, then verify.")
    elif step == "login":
        if not sys.stdin.isatty():
            raise SystemExit("Open this login step in Jamaica's interactive terminal.")
        run(uv, "run", "--script", str(BRIDGE), "login", "all")
    else:
        check_plugin(codex)
        return subprocess.run([sys.executable, str(REPO / "scripts/check_hermes_connection.py")], cwd=REPO).returncode
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"A setup command stopped (exit {exc.returncode}). Resolve the reported step in SETUP.md and resume.")
