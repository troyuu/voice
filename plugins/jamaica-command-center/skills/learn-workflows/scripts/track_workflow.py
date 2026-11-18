#!/usr/bin/env python3
"""Track privacy-safe repeated workflow counts in Jamaica's ignored runtime state."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
import re
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

import helper_agent

PRIVATE_HISTORY = Path.home() / ".local/share/jamaica-command-center/runtime/workflow-history.json"

SAFE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def command(name, help_text):
        sub = subparsers.add_parser(name, help=help_text)
        sub.add_argument("--history", type=Path, default=PRIVATE_HISTORY)
        sub.add_argument("--workflow-id", required=True)
        return sub

    record = command("record", "Record one workflow attempt")
    record.add_argument("--summary", help="Optional generic label; defaults to the workflow ID")
    record.add_argument("--run-id", type=uuid.UUID, help="Opaque UUID for this completed task, reused on retry")
    outcome = record.add_mutually_exclusive_group(required=True)
    outcome.add_argument("--success", action="store_true")
    outcome.add_argument("--failed", action="store_true")

    command("status", "Show one workflow's status")
    proposed = command("mark-proposed", "Mark a tested non-agent workflow as proposed")
    proposed.add_argument("--requested", action="store_true", help="Jamaica directly requested this workflow")
    draft = command("draft-agent", "Prepare a private helper file for sample review")
    draft.add_argument("--requested", action="store_true", help="Jamaica directly requested a helper")
    draft.add_argument("--role", choices=helper_agent.ROLES, required=True)
    draft.add_argument("--purpose", required=True)
    draft.add_argument("--step", action="append", required=True)
    draft.add_argument("--result", required=True)
    review = command("check-review", "Check the sample review before asking Jamaica about activation")
    review.add_argument("--sha256", required=True)
    enable = command("enable-agent", "Install only after Jamaica approves the tested version")
    enable.add_argument("--approved-sha256", required=True)
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
    if (not SAFE_ID.fullmatch(workflow_id) or len(workflow_id) > 48
            or re.fullmatch(r"con|prn|aux|nul|com[1-9]|lpt[1-9]", workflow_id)):
        raise ValueError("workflow-id must use lowercase words separated by hyphens")


def safe_summary(summary: str) -> str:
    value = " ".join(summary.split())
    if not value or len(value) > 120:
        raise ValueError("summary must contain 1 to 120 characters")
    if "@" in value or re.search(r"\+?\d[\d\s().-]{7,}\d", value):
        raise ValueError("summary must not contain an email address or phone number")
    return value


def save_history(path: Path, payload: dict) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write((json.dumps(payload, indent=2, sort_keys=True) + "\n").encode())
    os.replace(tmp.name, path)


@contextmanager
def history_lock(path):
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    with path.with_suffix(".lock").open("a+b") as lock:
        if os.name == "nt":
            import msvcrt
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX)
        yield  # Closing the handle releases the OS lock even on failure.


def workflow_status(entry: dict) -> dict:
    successes = int(entry.get("successful_runs", 0))
    return {
        "successful_runs": successes,
        "proposal_due": successes >= 3 and not entry.get("proposal_created", False) and "helper" not in entry,
        "proposal_created": bool(entry.get("proposal_created", False)),
        **({"helper": entry["helper"]} if "helper" in entry else {}),
    }


def update(args):
    history = load_history(args.history)
    workflows = history["workflows"]

    if args.command == "status":
        return workflow_status(workflows.get(args.workflow_id, {}))

    if args.command == "check-review":
        entry = workflows.get(args.workflow_id, {})
        helper_agent.reviewed_bytes(args.history, args.workflow_id, entry, args.sha256)
        return {"sample_review": "passed", "sha256": args.sha256, "hermes_role": entry["helper"]["role"]}

    if args.command == "draft-agent":
        entry = workflows.setdefault(args.workflow_id, {})
        if not (args.requested or workflow_status(entry)["proposal_due"] or entry.get("helper")):
            raise ValueError("Wait for three verified completions or Jamaica's direct request.")
        result = helper_agent.draft(args, entry)
        save_history(args.history, history)
        return result

    if args.command == "mark-proposed":
        entry = workflows.setdefault(args.workflow_id, {})
        if not args.requested and int(entry.get("successful_runs", 0)) < 3:
            raise ValueError("Wait for three verified completions or Jamaica's direct request.")
        entry["proposal_created"] = True
        entry["proposal_created_at"] = datetime.now(timezone.utc).isoformat()
        save_history(args.history, history)
        return workflow_status(entry)

    summary = safe_summary(args.summary or args.workflow_id.replace("-", " "))
    entry = workflows.setdefault(
        args.workflow_id,
        {"summary": summary, "successful_runs": 0, "failed_runs": 0, "proposal_created": False},
    )
    if args.run_id and args.success:
        receipts = entry.setdefault("success_receipts", [])
        receipt = args.run_id.hex
        if receipt in receipts:
            return workflow_status(entry)
        receipts.append(receipt)
    entry["summary"] = summary
    key = "successful_runs" if args.success else "failed_runs"
    entry[key] = int(entry.get(key, 0)) + 1
    entry["last_recorded_at"] = datetime.now(timezone.utc).isoformat()
    save_history(args.history, history)
    return workflow_status(entry)


def main():
    args = parse_args()
    validate_id(args.workflow_id)
    if args.command == "enable-agent":
        # The history snapshot and draft are digest-checked. Don't lock other workflows during a model call.
        entry = load_history(args.history)["workflows"].get(args.workflow_id, {})
        result = helper_agent.enable(args.history, args.workflow_id, entry, args.approved_sha256)
    else:
        with history_lock(args.history):
            result = update(args)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        sys.exit(str(exc))
