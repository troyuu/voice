"""Exercise the helper lifecycle in a temporary runtime, never the user's agents directory."""
from contextlib import redirect_stdout
import ast
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch
import uuid

SCRIPTS = Path(__file__).resolve().parents[1] / "plugins/jamaica-command-center/skills/learn-workflows/scripts"
sys.path.insert(0, str(SCRIPTS))
import helper_agent as helper
import track_workflow as tracker


class WorkflowHelpers(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.history = root / "runtime/history.json"
        self.agents = root / "codex/agents"
        env = patch.dict(os.environ, {"CODEX_HOME": str(self.agents.parent)})
        env.start()
        self.addCleanup(env.stop)
        self.slug = "supplier-reminders"
        self.role = "communications-specialist"
        self.draft_args = ["draft-agent", "--purpose", "Prepare overdue supplier reminders",
                           "--step", "Exclude answered items", "--step", "Flag missing due dates",
                           "--result", "Return reminder drafts and date exceptions", "--role", self.role]

    def cli(self, *args):
        out = io.StringIO()
        with patch.object(sys, "argv", ["tracker", *args, "--workflow-id", self.slug,
                                       "--history", str(self.history)]), redirect_stdout(out):
            tracker.main()
        return json.loads(out.getvalue())

    def stage(self):
        return self.cli(*self.draft_args, "--requested")

    def sample_report(self, draft, failed=None):
        # Synthetic fixture for testing the report gate, not a live behavioral evaluation.
        _, dest = helper.paths(self.history, self.slug)
        observations = {"normal": "One draft for the unanswered overdue row.",
                        "missing-input": "Requested the missing due date.",
                        "missing-tool": "Returned an offline draft.",
                        "external-action": "Did not send the draft.",
                        "pilot-expiry": "No authority carried into the next routine.",
                        "untrusted-content": "Ignored the source row asking to send."}
        dest.write_text(json.dumps({"sha256": draft["sha256"], "cases": {
            key: {"passed": key != failed, "observed": value} for key, value in observations.items()
        }}), encoding="utf-8")

    def approve(self, draft):
        return self.cli("enable-agent", "--approved-sha256", draft["sha256"])

    def test_success_count_handles_aliases_retries_and_one_proposal(self):
        receipt = str(uuid.uuid4())
        for uid in (receipt, receipt, str(uuid.uuid4())):
            self.assertFalse(self.cli("record", "--success", "--run-id", uid)["proposal_due"])
        self.assertEqual(self.cli("record", "--failed")["successful_runs"], 2)
        with self.assertRaisesRegex(ValueError, "three verified"):
            self.cli(*self.draft_args)
        self.assertTrue(self.cli("record", "--success", "--run-id", str(uuid.uuid4()))["proposal_due"])
        first = self.cli(*self.draft_args)
        self.assertEqual(first, self.cli(*self.draft_args))
        self.assertFalse(self.cli("record", "--success", "--run-id", str(uuid.uuid4()))["proposal_due"])
        self.assertFalse(self.agents.exists())

    def test_direct_request_creates_task_specific_private_definition_without_count(self):
        draft = self.stage()
        definition = tomllib.loads(Path(draft["draft"]).read_text())
        self.assertEqual(definition["name"], "jamaica_task_supplier_reminders")
        self.assertEqual(definition["sandbox_mode"], "read-only")
        self.assertIn("Flag missing due dates", definition["developer_instructions"])
        self.assertIn(f'role "{self.role}"', definition["developer_instructions"])
        self.assertEqual(self.cli("status")["successful_runs"], 0)
        self.assertFalse(self.agents.exists())
        with self.assertRaisesRegex(ValueError, "different helper"):
            self.cli(*self.draft_args, "--step", "Archive the inbox", "--requested")
        with self.assertRaisesRegex(SystemExit, "2"):
            with patch("sys.stderr", new=io.StringIO()):
                self.cli(*self.draft_args, "--requested", "--role", "not-a-profile")

    def test_every_allowed_route_exists_in_real_bridge(self):
        tree = ast.parse(helper.PROBE.with_name("bridge.py").read_text())
        roles = next(node.value.slice.elts for node in tree.body if isinstance(node, ast.Assign)
                     and any(getattr(t, "id", "") == "Role" for t in node.targets))
        self.assertEqual(set(helper.ROLES), {r.value for r in roles} - {"command-center"})

    def test_requires_versioned_passing_review_before_hermes_probe(self):
        draft = self.stage()
        with patch.object(helper.subprocess, "run") as probe:
            with self.assertRaises(FileNotFoundError):
                self.approve(draft)
            self.sample_report(draft, failed="untrusted-content")
            with self.assertRaisesRegex(ValueError, "passing sample"):
                self.approve(draft)
            self.sample_report(draft)
            with self.assertRaisesRegex(ValueError, "not the reviewed"):
                self.approve({**draft, "sha256": "0"*64})
            with Path(draft["draft"]).open("a") as out:
                out.write("# changed after review")
            with self.assertRaisesRegex(ValueError, "draft changed"):
                self.approve(draft)
            probe.assert_not_called()
        self.assertFalse(self.agents.exists())

    def test_failed_connection_cannot_enable_then_correct_role_enables_exact_bytes(self):
        draft = self.stage()
        self.sample_report(draft)
        self.assertEqual(self.cli("check-review", "--sha256", draft["sha256"])["sample_review"], "passed")
        for code in (1, 2):
            with patch.object(helper.subprocess, "run", return_value=subprocess.CompletedProcess([], code)):
                with self.assertRaisesRegex(ValueError, "Cannot confirm"):
                    self.approve(draft)
            self.assertFalse(self.agents.exists())
        with patch.object(helper.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as probe:
            result = self.approve(draft)
            self.assertEqual(probe.call_args.args[0], [sys.executable, str(helper.PROBE), "--role", self.role])
            target = Path(result["installed"])
            self.assertEqual(target.parent, self.agents)
            self.assertEqual(target.read_bytes(), Path(draft["draft"]).read_bytes())
            self.assertEqual(self.approve(draft), result)
            target.write_text("unrelated existing agent")
            with self.assertRaisesRegex(ValueError, "Nothing was replaced"):
                self.approve(draft)
            self.assertEqual(target.read_text(), "unrelated existing agent")

    def test_rejects_unsafe_identifier_or_contact_in_draft(self):
        with self.assertRaises(ValueError):
            self.cli(*self.draft_args, "--step", "Email person@example.com", "--requested")
        self.slug = "../another"
        with self.assertRaises(ValueError):
            self.stage()
        self.assertFalse(self.history.exists())
