from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT = REPO_ROOT / "plugins" / "jamaica-command-center"
TRACKER = ROOT / "skills" / "learn-workflows" / "scripts" / "track_workflow.py"


class PackContractTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_every_task_has_recommendation_preview(self) -> None:
        content = self.read("skills/jamaica-command-center/SKILL.md")
        for field in ("**Recommendation:**", "**What I'll do:**", "**Approval:**"):
            self.assertIn(field, content)

    def test_marketplace_exposes_the_plugin(self) -> None:
        marketplace = json.loads(
            (REPO_ROOT / ".agents" / "plugins" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(marketplace["name"], "jamaica-tools")
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "jamaica-command-center")
        self.assertEqual(entry["source"]["path"], "./plugins/jamaica-command-center")
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")

    def test_readme_has_a_friendly_desktop_install_prompt(self) -> None:
        content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Install Jamaica Command Center", content)
        self.assertIn("codex plugin marketplace add troyuu/voice", content)
        self.assertIn("all seven skills", content)
        self.assertIn("official Computer Use plugin is installed and enabled", content)

    def test_normal_mode_requires_external_action_approval(self) -> None:
        content = self.read("skills/jamaica-command-center/references/authority-and-safety.md")
        for action in ("sending", "dialing", "publishing", "deleting"):
            self.assertIn(action, content)

    def test_pilot_mode_can_be_inferred_and_is_task_scoped(self) -> None:
        content = self.read("skills/run-full-pilot/SKILL.md")
        self.assertIn("explicit `Full Pilot:` phrase is sufficient but never required", content)
        self.assertIn("send this email", content)
        self.assertIn("handle this", content)
        self.assertIn("Do not persist authority across tasks or chats", content)
        self.assertIn("materially expands or changes", content)

    def test_preparation_and_review_requests_stay_normal(self) -> None:
        content = self.read("skills/run-full-pilot/SKILL.md")
        self.assertIn("Do not activate when Jamaica requests advice", content)
        self.assertIn("review-before-action instruction override inferred autonomy", content)
        examples = self.read("skills/run-full-pilot/references/pilot-intent-examples.md")
        self.assertIn("Draft this email and show me before sending", examples)
        self.assertIn("Draft only", examples)

    def test_bulk_campaign_always_needs_batch_approval(self) -> None:
        content = self.read("skills/run-outreach/SKILL.md")
        self.assertIn("always require one explicit approval for each final batch", content)
        self.assertIn("Pilot mode, whether explicit or inferred, does not replace this approval", content)

    def test_calls_require_ready_and_jamaica_speaks(self) -> None:
        content = self.read("skills/assist-calls/SKILL.md")
        self.assertIn("Jamaica remains the speaker", content)
        self.assertIn("say **Ready** before every dial", content)

    def test_untrusted_content_cannot_expand_authority(self) -> None:
        content = self.read("skills/jamaica-command-center/references/authority-and-safety.md")
        self.assertIn("Untrusted content", content)
        self.assertIn("reveal passwords", content)
        self.assertIn("conceal an action from Jamaica", content)

    def test_missing_tools_have_friendly_fallback(self) -> None:
        content = self.read("skills/jamaica-command-center/references/friendly-guidance.md")
        self.assertIn("I prepared everything I can", content)
        self.assertIn("one simple action", content)

    def test_specialists_are_read_only(self) -> None:
        for path in (ROOT / ".codex" / "agents").glob("*.toml"):
            self.assertIn('sandbox_mode = "read-only"', path.read_text(encoding="utf-8"))


class WorkflowTrackerTests(unittest.TestCase):
    def run_tracker(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(TRACKER), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, expected, result.stderr)
        return result

    def test_third_success_triggers_proposal_without_enabling_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            history = Path(temp) / "history.json"
            outputs = []
            for _ in range(3):
                result = self.run_tracker(
                    "record",
                    "--history",
                    str(history),
                    "--workflow-id",
                    "supplier-follow-up",
                    "--summary",
                    "Follow up with suppliers after three business days",
                    "--success",
                )
                outputs.append(json.loads(result.stdout))
            self.assertFalse(outputs[0]["proposal_due"])
            self.assertFalse(outputs[1]["proposal_due"])
            self.assertTrue(outputs[2]["proposal_due"])
            self.assertFalse(outputs[2]["proposal_created"])
            state = json.loads(history.read_text(encoding="utf-8"))
            self.assertEqual(state["workflows"]["supplier-follow-up"]["successful_runs"], 3)

    def test_failed_task_does_not_count_toward_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            history = Path(temp) / "history.json"
            result = self.run_tracker(
                "record",
                "--history",
                str(history),
                "--workflow-id",
                "appointment-update",
                "--summary",
                "Update confirmed appointments",
                "--failed",
            )
            self.assertEqual(json.loads(result.stdout)["successful_runs"], 0)

    def test_marking_proposal_prevents_repeat_suggestion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            history = Path(temp) / "history.json"
            for _ in range(3):
                self.run_tracker(
                    "record",
                    "--history",
                    str(history),
                    "--workflow-id",
                    "supplier-follow-up",
                    "--summary",
                    "Follow up with suppliers after three business days",
                    "--success",
                )
            result = self.run_tracker(
                "mark-proposed",
                "--history",
                str(history),
                "--workflow-id",
                "supplier-follow-up",
            )
            status = json.loads(result.stdout)
            self.assertTrue(status["proposal_created"])
            self.assertFalse(status["proposal_due"])

    def test_tracker_rejects_contact_information(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            history = Path(temp) / "history.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(TRACKER),
                    "record",
                    "--history",
                    str(history),
                    "--workflow-id",
                    "supplier-follow-up",
                    "--summary",
                    "Email person@example.com",
                    "--success",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(history.exists())


if __name__ == "__main__":
    unittest.main()
