import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("research_prep", Path(__file__).parents[1] / "foundry" / "dgx_research_prep.py")
prep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prep)


class PrepTests(unittest.TestCase):
    def test_trace_contract_renders_digest_and_both_typed_outcomes(self):
        digest = "sha256:" + "d" * 64
        contract = prep.trace_receipt_contract(digest)
        self.assertEqual(contract["copy_digest_byte_for_byte"], digest)
        self.assertIn(f"Frontier advice: {digest}; executed=yes;", contract["verified_line_if_executed"])
        self.assertIn(f"Frontier advice: {digest}; executed=no;", contract["verified_line_if_not_executed"])
        self.assertIsNone(prep.trace_receipt_contract(None))

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
                    "semantic_contract_digest": "sha256:" + "c" * 64,
                    "runtime_telemetry": {"status": "over_budget"},
                },
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            path.write_text(json.dumps(state))
            feedback = prep.latest_quarantine_feedback(path, "target")
        self.assertEqual(feedback["frontier_id"], "target")
        self.assertEqual(feedback["errors"], ["scope overclaim"])
        self.assertEqual(
            feedback["semantic_contract_digest"], "sha256:" + "c" * 64
        )
        self.assertEqual(feedback["runtime_telemetry"]["status"], "over_budget")

    def test_latest_continuation_requires_accepted_source_hash(self):
        accepted_sha = "a" * 64
        rejected_sha = "b" * 64
        state = {
            "accepted": {"job/accepted.md": accepted_sha},
            "rejected": {"job/rejected.md": rejected_sha},
        }
        receipts = [
            {
                "receipt_id": "sha256:" + "1" * 64,
                "frontier_id": "target",
                "occurred_at": "2026-07-15T07:00:00Z",
                "classification": "progress",
                "action": "completed exact verifier",
                "result": "bounded verifier result",
                "next_gate": "implement one canonical augmentation primitive",
                "source": {
                    "job_id": "job",
                    "run_file": "accepted.md",
                    "sha256": accepted_sha,
                },
            },
            {
                "receipt_id": "sha256:" + "2" * 64,
                "frontier_id": "target",
                "occurred_at": "2026-07-15T08:00:00Z",
                "classification": "progress",
                "action": "unadmitted newer action",
                "result": "must not cross",
                "next_gate": "wrong gate",
                "source": {
                    "job_id": "job",
                    "run_file": "rejected.md",
                    "sha256": rejected_sha,
                },
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipts_root = root / "receipts"
            receipts_root.mkdir()
            for index, receipt in enumerate(receipts):
                (receipts_root / f"{index}.json").write_text(json.dumps(receipt))
            state_path = root / "state.json"
            state_path.write_text(json.dumps(state))
            continuation = prep.latest_accepted_continuation(
                receipts_root, state_path, "target"
            )
        self.assertEqual(continuation["completed_action"], "completed exact verifier")
        self.assertEqual(
            continuation["next_gate"],
            "implement one canonical augmentation primitive",
        )
        self.assertEqual(continuation["source"]["sha256"], accepted_sha)

    def test_continuation_instruction_makes_prior_action_nonrepeatable(self):
        instruction = prep.continuation_instruction({"receipt_id": "sha256:fixture"})
        self.assertIn("not tasks to repeat", instruction)
        self.assertIn("Continue from its next_gate", instruction)
        self.assertIn("continuation wins", instruction)
        self.assertEqual(prep.continuation_instruction(None), "")

    def test_runtime_quarantine_shrinks_instead_of_replaying_route(self):
        runtime = prep.quarantine_instruction(
            {"runtime_telemetry": {"status": "over_budget"}}
        )
        semantic = prep.quarantine_instruction({"errors": ["scope overclaim"]})
        self.assertIn("shrink the action and context", runtime)
        self.assertIn("do not repeat the over-budget route", runtime)
        self.assertNotIn("Replay the bounded evidence", runtime)
        self.assertIn("Replay the bounded evidence", semantic)
        self.assertEqual(prep.quarantine_instruction(None), "")


if __name__ == "__main__":
    unittest.main()
