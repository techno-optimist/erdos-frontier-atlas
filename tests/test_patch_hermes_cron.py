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
    def test_patch_is_exact_idempotent_and_only_lowers_global_cap(self):
        original = "prefix\n" + patcher.OLD + "suffix\n"
        patched, changed = patcher.patch_text(original)
        self.assertTrue(changed)
        self.assertIn(patcher.MARKER, patched)
        self.assertIn("min(_global_max_iterations", patched)
        repeated, changed_again = patcher.patch_text(patched)
        self.assertFalse(changed_again)
        self.assertEqual(repeated, patched)

    def test_unknown_scheduler_source_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "source drifted"):
            patcher.patch_text("unrecognized scheduler")

    def test_file_install_preserves_backup_and_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scheduler.py"
            path.write_text(
                "def run(job, _cfg):\n    if True:\n"
                + patcher.OLD
                + "        return max_iterations\n"
            )
            path.chmod(0o640)
            result = patcher.patch_file(path)
            self.assertTrue(result["changed"])
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            self.assertTrue(Path(result["backup"]).exists())
            self.assertEqual(len(result["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
