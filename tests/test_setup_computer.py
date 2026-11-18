from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import setup_computer as setup


class InstallerTests(unittest.TestCase):
    def test_new_clone_registers_then_installs_verified_skills(self):
        calls = []

        def fake_codex(*args, capture=False):
            calls.append(args[1:4])
            if args[1:4] == ("plugin", "marketplace", "list"):
                return {"marketplaces": []}
            if args[1:3] == ("plugin", "add"):
                return {"version": setup.VERSION, "installedPath": str(setup.PACKAGE)}
            if args[1:3] == ("plugin", "list"):
                return {"installed": [{"pluginId": "jamaica-command-center@jamaica-tools",
                        "version": setup.VERSION, "installed": True, "enabled": True}]}

        with patch.object(setup, "run", side_effect=fake_codex):
            setup.install_plugin("codex")
        self.assertIn(("plugin", "marketplace", "add"), calls)

    def test_zip_install_never_refreshes_a_remote_project_copy(self):
        with tempfile.TemporaryDirectory() as folder:
            store = {"name": setup.MARKET, "root": str(Path(folder) / "older"),
                     "marketplaceSource": {"sourceType": "git", "source": "https://github.com/troyuu/voice.git"}}
            with patch.object(setup, "REPO", Path(folder)), patch.object(setup, "run", return_value={"marketplaces": [store]}) as runner:
                with self.assertRaisesRegex(SystemExit, "supplied local folder"):
                    setup.install_plugin("codex")
                self.assertEqual(runner.call_count, 1)

    def test_foreign_marketplace_is_preserved(self):
        with tempfile.TemporaryDirectory() as other:
            store = {"name": setup.MARKET, "root": other, "marketplaceSource": {"sourceType": "local"}}
            with patch.object(setup, "run", return_value={"marketplaces": [store]}) as runner:
                with self.assertRaisesRegex(SystemExit, "another folder"):
                    setup.install_plugin("codex")
                self.assertEqual(runner.call_count, 1)

    def test_corrupt_installer_stops_before_execution(self):
        from io import BytesIO
        with tempfile.TemporaryDirectory() as tmp, patch.object(setup, "HERMES_HOME", Path(tmp) / "private"), \
             patch.object(setup.Path, "home", return_value=Path(tmp)), \
             patch.dict(setup.os.environ, {"LOCALAPPDATA": tmp}), \
             patch.object(setup.shutil, "which", return_value=None), \
             patch.object(setup, "urlopen", return_value=BytesIO(b"wrong content")), \
             patch.object(setup, "run") as runner:
            with self.assertRaisesRegex(SystemExit, "checksum"):
                setup.ensure_hermes()
            runner.assert_not_called()
            self.assertFalse(setup.HERMES_HOME.exists())
