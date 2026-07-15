import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("select_frontier", Path(__file__).parents[1] / "foundry" / "select_frontier.py")
selector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(selector)


class SelectorTests(unittest.TestCase):
    def test_recent_closed_lane_rotates_to_older_equal_priority_lane(self):
        queue = {"items": [
            {"id": "recent", "priority": 0.16, "last_context_at": "2026-07-15T03:30:00Z", "status": "control_plane_only"},
            {"id": "older", "priority": 0.16, "last_context_at": "2026-07-14T17:30:00Z", "status": "control_plane_only"},
        ]}
        ranked = selector.rank_items(queue, datetime(2026, 7, 15, 4, 0, tzinfo=timezone.utc))
        self.assertEqual(ranked[0]["frontier_id"], "older")

    def test_real_progress_can_beat_closed_lane(self):
        queue = {"items": [
            {"id": "progress", "priority": 0.16, "last_context_at": "2026-07-15T00:00:00Z", "status": "verified_progress"},
            {"id": "closed", "priority": 0.16, "last_context_at": "2026-07-15T00:00:00Z", "status": "closed_rotate"},
        ]}
        ranked = selector.rank_items(queue, datetime(2026, 7, 15, 4, 0, tzinfo=timezone.utc))
        self.assertEqual(ranked[0]["frontier_id"], "progress")


if __name__ == "__main__":
    unittest.main()
