import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("foundry_tick", ROOT / "tools" / "foundry_tick.py")
foundry_tick = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(foundry_tick)


class FoundryTickTests(unittest.TestCase):
    def test_exact_accepted_or_rejected_hash_is_skipped(self):
        state = {
            "accepted": {"job/accepted.md": "aaa"},
            "rejected": {"job/rejected.md": "bbb"},
        }
        self.assertTrue(foundry_tick.source_is_watermarked(state, "job/accepted.md", "aaa"))
        self.assertTrue(foundry_tick.source_is_watermarked(state, "job/rejected.md", "bbb"))

    def test_changed_or_unseen_source_is_reprocessed(self):
        state = {"accepted": {"job/run.md": "old"}, "rejected": {}}
        self.assertFalse(foundry_tick.source_is_watermarked(state, "job/run.md", "new"))
        self.assertFalse(foundry_tick.source_is_watermarked(state, "job/unseen.md", "new"))


if __name__ == "__main__":
    unittest.main()
