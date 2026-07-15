import importlib.util
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


if __name__ == "__main__":
    unittest.main()
