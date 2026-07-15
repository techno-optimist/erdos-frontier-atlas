import importlib.util
import io
import os
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
                    target = Path(cmd[cmd.index("--output") + 1])
                    target.write_text("{}\n")
                return mock.Mock(returncode=0, stdout="")

            with (
                mock.patch.object(tick, "STATE", state),
                mock.patch.object(tick, "REVIEWED_SKILL", reviewed),
                mock.patch.object(tick, "INSTALLED_SKILL", installed),
                mock.patch.object(tick.subprocess, "run", side_effect=fake_run) as run,
            ):
                self.assertEqual(tick.main(), 0)
            self.assertEqual(run.call_count, 2)
            first = " ".join(map(str, run.call_args_list[0].args[0]))
            second = " ".join(map(str, run.call_args_list[1].args[0]))
            self.assertIn("foundry_efficiency.py", first)
            self.assertIn("foundry_tick.py", second)
            self.assertIn("--efficiency-report", second)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual(installed.read_text(), reviewed.read_text())
            self.assertEqual(installed.stat().st_mode & 0o777, 0o644)

    def test_publication_failure_does_not_publish_stale_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state"
            state.mkdir()
            reviewed = Path(tmp) / "reviewed" / "SKILL.md"
            installed = Path(tmp) / "installed" / "SKILL.md"
            reviewed.parent.mkdir(); reviewed.write_text("reviewed\n")
            def fake_run(cmd, **kwargs):
                if "foundry_efficiency.py" in " ".join(map(str, cmd)):
                    target = Path(cmd[cmd.index("--output") + 1])
                    target.write_text("{}\n")
                    return mock.Mock(returncode=0, stdout="")
                return mock.Mock(returncode=7, stdout="publication failed\n")
            with (
                mock.patch.object(tick, "STATE", state),
                mock.patch.object(tick, "REVIEWED_SKILL", reviewed),
                mock.patch.object(tick, "INSTALLED_SKILL", installed),
                mock.patch.object(tick.subprocess, "run", side_effect=fake_run) as run,
            ):
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(tick.main(), 7)
            self.assertEqual(run.call_count, 2)
            self.assertEqual(installed.read_text(), reviewed.read_text())

    def test_rotated_logs_are_supplied_oldest_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            current = Path(tmp) / "agent.log"
            rotated = Path(tmp) / "agent.log.1"
            rotated.write_text("old\n"); current.write_text("new\n")
            os.utime(rotated, (1, 1)); os.utime(current, (2, 2))
            with mock.patch.object(tick, "AGENT_LOG", current):
                paths = tick.agent_log_paths()
            self.assertEqual(paths, [rotated, current])


if __name__ == "__main__":
    unittest.main()
