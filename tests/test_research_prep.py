import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("research_prep", Path(__file__).parents[1] / "foundry" / "dgx_research_prep.py")
prep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prep)


class PrepTests(unittest.TestCase):
    def test_focused_context_is_primary_and_broader_packet_is_conditional(self):
        instruction = prep.worker_instruction("Load context_packet.md, fill experiment.json, run one bounded action")
        self.assertIn("Read focused_context.md first", instruction)
        self.assertIn("only if", instruction)
        self.assertEqual(instruction.count("Load context_packet.md"), 1)

    def test_first_allowed_stall_overrides_moving_top_rank(self):
        ranked = [{"frontier_id": "moving"}, {"frontier_id": "stuck"}, {"frontier_id": "later"}]
        gates = {
            "moving": {"frontier_call_allowed": False},
            "stuck": {"frontier_call_allowed": True, "frontier_id": "stuck"},
            "later": {"frontier_call_allowed": True, "frontier_id": "later"},
        }
        frontier_id, gate = prep.first_allowed_stall(ranked, gates.get)
        self.assertEqual(frontier_id, "stuck")
        self.assertEqual(gate["frontier_id"], "stuck")

    def test_latest_quarantine_feedback_is_scoped_to_selected_frontier(self):
        state = {
            "rejected_details": {
                "job/one.md": {
                    "schema": "p42-foundry-quarantine-feedback-v1",
                    "recorded_at": "2026-07-15T07:00:00Z",
                    "source_sha256": "a" * 64,
                    "frontier_id": "other",
                    "errors": ["other error"],
                },
                "job/two.md": {
                    "schema": "p42-foundry-quarantine-feedback-v1",
                    "recorded_at": "2026-07-15T08:00:00Z",
                    "source_sha256": "b" * 64,
                    "frontier_id": "target",
                    "errors": ["scope overclaim"],
                    "remediation": "replay and narrow",
                },
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            path.write_text(json.dumps(state))
            feedback = prep.latest_quarantine_feedback(path, "target")
        self.assertEqual(feedback["frontier_id"], "target")
        self.assertEqual(feedback["errors"], ["scope overclaim"])


if __name__ == "__main__":
    unittest.main()
