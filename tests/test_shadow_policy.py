import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("shadow", Path(__file__).parents[1] / "foundry" / "shadow_policy.py")
shadow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(shadow)


class ShadowPolicyTests(unittest.TestCase):
    def test_rewards_evidence_yield_without_control_claim(self):
        queue = {"items": [
            {"id": "productive", "priority": 0.16, "last_touched": "2026-07-15T00:00:00Z"},
            {"id": "blocked", "priority": 0.16, "last_touched": "2026-07-15T00:00:00Z"},
        ]}
        receipts = [
            {"frontier_id": "productive", "classification": "progress", "occurred_at": "2026-07-15T00:01:00Z"},
            {"frontier_id": "productive", "classification": "negative_result", "occurred_at": "2026-07-15T00:02:00Z"},
            {"frontier_id": "blocked", "classification": "blocked", "occurred_at": "2026-07-15T00:01:00Z"},
            {"frontier_id": "blocked", "classification": "blocked", "occurred_at": "2026-07-15T00:02:00Z"},
        ]
        ranked = shadow.rank_shadow(queue, receipts, datetime(2026, 7, 15, 1, tzinfo=timezone.utc))
        self.assertEqual(ranked[0]["frontier_id"], "productive")
        self.assertGreater(ranked[0]["posterior_yield"], ranked[1]["posterior_yield"])
        self.assertEqual(ranked[1]["repeat_block_penalty"], 0.03)

    def test_unseen_lane_receives_exploration_bonus(self):
        queue = {"items": [{"id": "seen", "priority": 0.1}, {"id": "unseen", "priority": 0.1}]}
        receipts = [{"frontier_id": "seen", "classification": "blocked", "occurred_at": "2026-07-15T00:01:00Z"}]
        ranked = shadow.rank_shadow(queue, receipts, datetime(2026, 7, 15, 1, tzinfo=timezone.utc))
        rows = {row["frontier_id"]: row for row in ranked}
        self.assertGreater(rows["unseen"]["exploration_bonus"], rows["seen"]["exploration_bonus"])


if __name__ == "__main__":
    unittest.main()
