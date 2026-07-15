import importlib.util
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "patch_hermes_cron",
    Path(__file__).parents[1] / "foundry" / "patch_hermes_cron.py",
)
patcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patcher)


class HermesCronPatchTests(unittest.TestCase):
    @staticmethod
    def scheduler_source():
        return (
            "import logging\n"
            "logger = logging.getLogger(__name__)\n"
            "def run(job, _cfg, agent, _cron_future):\n"
            "    if True:\n"
            + patcher.OLD
            + "        job_name = 'fixture'\n"
            + "        _cron_timeout = 600.0\n"
            + patcher.WALL_SETUP_OLD
            + "        try:\n"
            + "            if False:\n"
            + "                pass\n"
            + "            else:\n"
            + "                while True:\n"
            + "                    done = {_cron_future}\n"
            + "                    import time\n"
            + "                    time.sleep(0.002)\n"
            + patcher.WALL_LOOP_OLD
            + "                    _idle_secs = 0.0\n"
            + "        except Exception:\n"
            + "            raise\n"
            + "        return max_iterations\n"
        )

    def test_patch_is_exact_idempotent_and_only_lowers_global_cap(self):
        original = self.scheduler_source()
        patched, changed = patcher.patch_text(original)
        self.assertTrue(changed)
        self.assertIn(patcher.MARKER, patched)
        self.assertIn(patcher.WALL_MARKER, patched)
        self.assertIn("min(_global_max_iterations", patched)
        repeated, changed_again = patcher.patch_text(patched)
        self.assertFalse(changed_again)
        self.assertEqual(repeated, patched)

    def test_unknown_scheduler_source_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "source drifted"):
            patcher.patch_text("unrecognized scheduler")

    def test_existing_turn_patch_upgrades_to_wall_cap(self):
        source = self.scheduler_source().replace(patcher.OLD, patcher.NEW)
        patched, changed = patcher.patch_text(source)
        self.assertTrue(changed)
        self.assertEqual(patched.count(patcher.MARKER), 1)
        self.assertEqual(patched.count(patcher.WALL_MARKER), 1)

    def test_wall_cap_is_opt_in_and_fails_closed_on_invalid_values(self):
        namespace = {}
        patched, _ = patcher.patch_text(self.scheduler_source())
        exec(compile(patched, "scheduler.py", "exec"), namespace)

        class Agent:
            interrupted = None

            def interrupt(self, reason):
                self.interrupted = reason

        class Future:
            def result(self):
                return {"ok": True}

        run = namespace["run"]
        self.assertEqual(run({}, {"agent": {"max_turns": 100}}, Agent(), Future()), 100)
        with self.assertRaisesRegex(RuntimeError, "finite positive"):
            run({"max_wall_seconds": 0}, {}, Agent(), Future())
        agent = Agent()
        with self.assertRaisesRegex(TimeoutError, "exceeded wall limit"):
            run({"max_wall_seconds": 0.001}, {}, agent, Future())
        self.assertEqual(agent.interrupted, "Cron job timed out (wall limit)")

    def test_file_install_preserves_backup_and_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scheduler.py"
            path.write_text(self.scheduler_source())
            path.chmod(0o640)
            result = patcher.patch_file(path)
            self.assertTrue(result["changed"])
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            self.assertTrue(Path(result["backup"]).exists())
            self.assertEqual(len(result["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
