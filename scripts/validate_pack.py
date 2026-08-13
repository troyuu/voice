#!/usr/bin/env python3
"""Validate the portable Jamaica Command Center source package."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover - Python version guard
    raise SystemExit("Python 3.11 or newer is required") from exc

REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "plugins" / "jamaica-command-center"
MARKETPLACE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
AGENT_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
REQUIRED_PREVIEW = ("Recommendation", "What I'll do", "Approval")
ALWAYS_PAUSE_TERMS = (
    "credentials",
    "payments",
    "contracts",
    "permission changes",
    "destructive actions",
    "sensitive disclosures",
    "bulk outreach approval",
    "Ready",
)
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub-style token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--marketplace", type=Path, default=MARKETPLACE)
    return parser.parse_args()


def load_interface_yaml(path: Path, errors: list[str]) -> dict | None:
    """Parse the deliberately small agents/openai.yaml interface shape."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        errors.append(f"{path}: unable to read YAML: {exc}")
        return None
    if not lines or lines[0].strip() != "interface:":
        errors.append(f"{path}: expected a top-level interface object")
        return None
    interface: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        if not line.startswith("  ") or ":" not in line:
            errors.append(f"{path}:{line_number}: invalid interface YAML line")
            continue
        key, raw_value = line.strip().split(":", 1)
        raw_value = raw_value.strip()
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            errors.append(f"{path}:{line_number}: interface values must be quoted strings")
            continue
        if not isinstance(value, str) or not value:
            errors.append(f"{path}:{line_number}: interface value must be a non-empty string")
            continue
        interface[key] = value
    required = {"display_name", "short_description", "default_prompt"}
    missing = required - set(interface)
    if missing:
        errors.append(f"{path}: missing interface fields: {', '.join(sorted(missing))}")
    return {"interface": interface}


def split_frontmatter(path: Path, errors: list[str]) -> tuple[dict, str] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{path}: missing YAML frontmatter")
        return None
    try:
        raw, body = text[4:].split("\n---\n", 1)
        metadata: dict[str, str] = {}
        for line in raw.splitlines():
            if not line.strip() or ":" not in line:
                raise ValueError("frontmatter must use one key-value pair per line")
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{path}: invalid frontmatter: {exc}")
        return None
    if not isinstance(metadata, dict):
        errors.append(f"{path}: frontmatter must be an object")
        return None
    return metadata, body


def validate_manifest(root: Path, errors: list[str]) -> None:
    path = root / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{path}: invalid JSON: {exc}")
        return
    required = ("name", "version", "description", "author", "skills", "interface")
    for key in required:
        if key not in manifest:
            errors.append(f"{path}: missing {key}")
    if manifest.get("name") != root.name:
        errors.append(f"{path}: plugin name must match folder name")
    if manifest.get("skills") != "./skills/":
        errors.append(f"{path}: skills path must be ./skills/")


def validate_marketplace(path: Path, root: Path, errors: list[str]) -> None:
    try:
        marketplace = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"{path}: invalid JSON: {exc}")
        return
    if marketplace.get("name") != "jamaica-tools":
        errors.append(f"{path}: marketplace name must be jamaica-tools")
    if marketplace.get("interface", {}).get("displayName") != "Jamaica Tools":
        errors.append(f"{path}: marketplace display name must be Jamaica Tools")
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        errors.append(f"{path}: expected exactly one plugin entry")
        return
    entry = entries[0]
    expected_path = "./plugins/jamaica-command-center"
    if entry.get("name") != root.name:
        errors.append(f"{path}: plugin entry name must match the plugin folder")
    if entry.get("source") != {"source": "local", "path": expected_path}:
        errors.append(f"{path}: source must point to {expected_path}")
    if entry.get("policy") != {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }:
        errors.append(f"{path}: plugin policy is invalid")
    if entry.get("category") != "Productivity":
        errors.append(f"{path}: plugin category must be Productivity")


def validate_skills(root: Path, errors: list[str]) -> None:
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    if not skills:
        errors.append("No skills found")
        return
    for path in skills:
        parsed = split_frontmatter(path, errors)
        if parsed is None:
            continue
        metadata, body = parsed
        if set(metadata) != {"name", "description"}:
            errors.append(f"{path}: frontmatter must contain only name and description")
        name = metadata.get("name")
        if name != path.parent.name or not isinstance(name, str) or not NAME_RE.fullmatch(name):
            errors.append(f"{path}: invalid or mismatched skill name")
        description = metadata.get("description")
        if not isinstance(description, str) or len(description.strip()) < 40:
            errors.append(f"{path}: description is too short")
        todo_marker = "[" + "TODO:"
        if todo_marker in path.read_text(encoding="utf-8"):
            errors.append(f"{path}: contains an unfinished placeholder")
        if path.parent.name == "jamaica-command-center":
            for heading in REQUIRED_PREVIEW:
                if heading not in body:
                    errors.append(f"{path}: missing preview field {heading}")
        interface_path = path.parent / "agents" / "openai.yaml"
        interface = load_interface_yaml(interface_path, errors)
        if interface:
            prompt = interface.get("interface", {}).get("default_prompt", "")
            if f"${name}" not in prompt:
                errors.append(f"{interface_path}: default_prompt must mention ${name}")


def validate_agents(root: Path, errors: list[str]) -> None:
    agents = sorted((root / ".codex" / "agents").glob("*.toml"))
    expected = {
        "communications_specialist",
        "call_specialist",
        "operations_specialist",
        "research_specialist",
        "workflow_designer",
        "risk_reviewer",
    }
    found: set[str] = set()
    for path in agents:
        try:
            payload = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: invalid TOML: {exc}")
            continue
        for field in ("name", "description", "developer_instructions"):
            if not isinstance(payload.get(field), str) or not payload[field].strip():
                errors.append(f"{path}: missing {field}")
        name = payload.get("name", "")
        if not AGENT_NAME_RE.fullmatch(name):
            errors.append(f"{path}: invalid agent name")
        found.add(name)
        if payload.get("sandbox_mode") != "read-only":
            errors.append(f"{path}: specialist agents must be read-only")
    missing = expected - found
    if missing:
        errors.append(f"Missing specialist agents: {', '.join(sorted(missing))}")


def validate_contract(root: Path, errors: list[str]) -> None:
    agents_text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    full_pilot = (root / "skills" / "run-full-pilot" / "SKILL.md").read_text(encoding="utf-8")
    outreach = (root / "skills" / "run-outreach" / "SKILL.md").read_text(encoding="utf-8")
    calls = (root / "skills" / "assist-calls" / "SKILL.md").read_text(encoding="utf-8")
    learning = (root / "skills" / "learn-workflows" / "SKILL.md").read_text(encoding="utf-8")

    for term in REQUIRED_PREVIEW:
        if term not in agents_text:
            errors.append(f"AGENTS.md: missing task preview term {term}")
    for term in ALWAYS_PAUSE_TERMS:
        if term not in agents_text:
            errors.append(f"AGENTS.md: missing approval boundary {term}")
    pilot_requirements = (
        "whether or not she says `Full Pilot`",
        "direct completion commands",
        "show me first",
        "materially changes",
    )
    for requirement in pilot_requirements:
        if requirement not in agents_text:
            errors.append(f"AGENTS.md: missing Pilot intent rule: {requirement}")
    if "always require one explicit approval" not in outreach:
        errors.append("run-outreach: exact batch approval rule is missing")
    if "say **Ready** before every dial" not in calls:
        errors.append("assist-calls: Ready-before-dial rule is missing")
    if "third substantially similar successful task" not in learning:
        errors.append("learn-workflows: three-success trigger is missing")
    if "explicit `Full Pilot:` phrase is sufficient but never required" not in full_pilot:
        errors.append("run-full-pilot: inferred Pilot activation rule is missing")
    if "explicit review-before-action instruction override inferred autonomy" not in full_pilot:
        errors.append("run-full-pilot: normal-mode override rule is missing")
    if "Do not persist authority across tasks or chats" not in full_pilot:
        errors.append("run-full-pilot: task-scoped expiry rule is missing")


def scan_public_files(repo_root: Path, plugin_root: Path, errors: list[str]) -> None:
    runtime_paths = (repo_root / "runtime", plugin_root / "runtime")
    for runtime in runtime_paths:
        if runtime.exists():
            errors.append(f"{runtime}: private runtime directory must not be in the public source pack")
    allowed_suffixes = {".md", ".json", ".yaml", ".yml", ".toml", ".py", ".txt", ""}
    for path in repo_root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() not in allowed_suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{path}: possible {label}")


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    validate_marketplace(args.marketplace.resolve(), root, errors)
    validate_manifest(root, errors)
    validate_skills(root, errors)
    validate_agents(root, errors)
    validate_contract(root, errors)
    scan_public_files(REPO_ROOT, root, errors)
    if errors:
        print("Jamaica Command Center validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    skill_count = len(list((root / "skills").glob("*/SKILL.md")))
    agent_count = len(list((root / ".codex" / "agents").glob("*.toml")))
    print(f"Validation passed: {skill_count} skills, {agent_count} specialist agents, no obvious secrets.")


if __name__ == "__main__":
    main()
