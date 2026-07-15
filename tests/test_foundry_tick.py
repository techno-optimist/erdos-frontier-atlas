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

    def test_rejection_detail_is_bounded_structured_feedback(self):
        inspection = {
            "source_sha256": "a" * 64,
            "receipt": {
                "receipt_id": "sha256:" + "b" * 64,
                "frontier_id": "erdos_1029_r55",
                "classification": "negative_result",
                "occurred_at": "2026-07-15T07:27:23Z",
            },
            "errors": ["semantic contract quantity-conflation claim: cyclic exhausted"],
        }
        detail = foundry_tick.rejection_detail(inspection, "fallback")
        self.assertEqual(detail["schema"], "p42-foundry-quarantine-feedback-v1")
        self.assertEqual(detail["frontier_id"], "erdos_1029_r55")
        self.assertEqual(detail["source_sha256"], "a" * 64)
        self.assertNotIn("run_file", detail)

    def test_legacy_hash_only_quarantine_can_be_tombstoned(self):
        detail = foundry_tick.rejection_detail({
            "source_sha256": "c" * 64,
            "receipt": None,
            "errors": ["legacy raw source unavailable; hash-only quarantine retained"],
        }, "fallback")
        self.assertEqual(detail["source_sha256"], "c" * 64)
        self.assertIsNone(detail["frontier_id"])
        self.assertIn("unavailable", detail["errors"][0])


if __name__ == "__main__":
    unittest.main()
