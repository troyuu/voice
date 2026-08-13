#!/usr/bin/env python3
"""Track privacy-safe repeated workflow counts in Jamaica's ignored runtime state."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


SAFE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    record = subparsers.add_parser("record", help="Record one workflow attempt")
    record.add_argument("--history", required=True, type=Path)
    record.add_argument("--workflow-id", required=True)
    record.add_argument("--summary", required=True)
    outcome = record.add_mutually_exclusive_group(required=True)
    outcome.add_argument("--success", action="store_true")
    outcome.add_argument("--failed", action="store_true")

    status = subparsers.add_parser("status", help="Show one workflow's status")
    status.add_argument("--history", required=True, type=Path)
    status.add_argument("--workflow-id", required=True)

    proposed = subparsers.add_parser("mark-proposed", help="Mark a tested proposal as created")
    proposed.add_argument("--history", required=True, type=Path)
    proposed.add_argument("--workflow-id", required=True)
    return parser.parse_args()


def load_history(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "workflows": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("workflows"), dict):
        raise ValueError("History must contain a workflows object")
    payload.setdefault("version", 1)
    return payload


def validate_id(workflow_id: str) -> None:
    if not SAFE_ID.fullmatch(workflow_id):
        raise ValueError("workflow-id must use lowercase words separated by hyphens")


def safe_summary(summary: str) -> str:
    value = " ".join(summary.split())
    if not value or len(value) > 120:
        raise ValueError("summary must contain 1 to 120 characters")
    if "@" in value or re.search(r"\+?\d[\d\s().-]{7,}\d", value):
        raise ValueError("summary must not contain an email address or phone number")
    return value


def save_history(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def workflow_status(entry: dict) -> dict:
    successes = int(entry.get("successful_runs", 0))
    return {
        "successful_runs": successes,
        "proposal_due": successes >= 3 and not bool(entry.get("proposal_created", False)),
        "proposal_created": bool(entry.get("proposal_created", False)),
    }


def main() -> None:
    args = parse_args()
    validate_id(args.workflow_id)
    history = load_history(args.history)
    workflows = history["workflows"]

    if args.command == "status":
        print(json.dumps(workflow_status(workflows.get(args.workflow_id, {})), sort_keys=True))
        return

    if args.command == "mark-proposed":
        if args.workflow_id not in workflows:
            raise ValueError("workflow-id has no recorded history")
        entry = workflows[args.workflow_id]
        if int(entry.get("successful_runs", 0)) < 3:
            raise ValueError("a proposal may be marked only after three successful runs")
        entry["proposal_created"] = True
        entry["proposal_created_at"] = datetime.now(timezone.utc).isoformat()
        save_history(args.history, history)
        print(json.dumps(workflow_status(entry), sort_keys=True))
        return

    summary = safe_summary(args.summary)
    entry = workflows.setdefault(
        args.workflow_id,
        {"summary": summary, "successful_runs": 0, "failed_runs": 0, "proposal_created": False},
    )
    entry["summary"] = summary
    key = "successful_runs" if args.success else "failed_runs"
    entry[key] = int(entry.get(key, 0)) + 1
    entry["last_recorded_at"] = datetime.now(timezone.utc).isoformat()
    save_history(args.history, history)
    print(json.dumps(workflow_status(entry), sort_keys=True))


if __name__ == "__main__":
    main()
