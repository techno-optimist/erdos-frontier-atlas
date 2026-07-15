import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

SPEC = importlib.util.spec_from_file_location(
    "dgx_tick", Path(__file__).parents[1] / "foundry" / "dgx_tick.py"
)
tick = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tick)


class DgxTickTests(unittest.TestCase):
    def test_successful_publication_refreshes_private_efficiency_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state"
            state.mkdir()
            output = state / "foundry_efficiency_latest.json"
            reviewed = Path(tmp) / "reviewed" / "SKILL.md"
            installed = Path(tmp) / "installed" / "SKILL.md"
            reviewed.parent.mkdir()
            reviewed.write_text("reviewed skill\n")

            def fake_run(cmd, **kwargs):
                if "foundry_efficiency.py" in " ".join(map(str, cmd)):
                    output.write_text("{}\n")
                return mock.Mock(returncode=0, stdout="")

            with (
                mock.patch.object(tick, "STATE", state),
                mock.patch.object(tick, "REVIEWED_SKILL", reviewed),
                mock.patch.object(tick, "INSTALLED_SKILL", installed),
                mock.patch.object(tick.subprocess, "run", side_effect=fake_run) as run,
            ):
                self.assertEqual(tick.main(), 0)
            self.assertEqual(run.call_count, 2)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual(installed.read_text(), reviewed.read_text())
            self.assertEqual(installed.stat().st_mode & 0o777, 0o644)

    def test_publication_failure_does_not_publish_stale_metrics(self):
        failed = mock.Mock(returncode=7, stdout="publication failed\n")
        with mock.patch.object(tick.subprocess, "run", return_value=failed) as run:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(tick.main(), 7)
        self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main()
