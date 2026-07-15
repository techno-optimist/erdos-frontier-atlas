import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[1]


class RsiProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = json.loads((ROOT / "foundry" / "rsi_protocol.json").read_text())
        cls.suite = json.loads((ROOT / "foundry" / "eval" / "public_suite.json").read_text())
        cls.atlas = json.loads((ROOT / "atlas" / "problems.json").read_text())

    def test_claim_stays_level_zero_until_evidence_gate(self):
        self.assertEqual(self.protocol["claim_status"]["current"], "level_0_delegated_search")
        self.assertFalse(self.protocol["promotion_gate"]["automatic_production_promotion"])
        self.assertFalse(self.protocol["adjudication"]["self_reported_receipt_classification_is_reward"])

    def test_checked_in_private_commitment_discloses_no_task_identity(self):
        commitment = json.loads(
            (ROOT / "foundry" / "eval" / "private_suite.commitment.json").read_text()
        )
        self.assertEqual(commitment["task_count"], self.protocol["evaluation"]["private_holdout_tasks"])
        self.assertFalse(commitment["task_ids_or_problem_ids_disclosed"])
        self.assertFalse(
            {"tasks", "task_ids", "problem_ids", "split_salt_hex"}
            & set(commitment)
        )

    def test_budget_is_fixed_and_frontier_free(self):
        budget = self.protocol["evaluation"]["budget_per_task_run"]
        self.assertGreater(budget["max_input_tokens"], 0)
        self.assertGreater(budget["max_api_calls"], 0)
        self.assertGreater(budget["max_wall_seconds"], 0)
        self.assertEqual(budget["max_frontier_calls"], 0)

    def test_public_suite_is_balanced_and_resolves_to_live_atlas(self):
        tasks = self.suite["tasks"]
        self.assertEqual(len(tasks), self.protocol["evaluation"]["public_development_tasks"])
        self.assertEqual(len({row["problem_id"] for row in tasks}), len(tasks))
        self.assertEqual(Counter(row["family"] for row in tasks), Counter({
            "exact_witness_or_backtracking": 2,
            "nonexistence_or_certificate": 2,
            "constructive_or_local_search": 2,
        }))
        atlas_by_id = {row["id"]: row for row in self.atlas["problems"]}
        self.assertTrue(all(row["problem_id"] in atlas_by_id for row in tasks))
        self.assertTrue(all(atlas_by_id[row["problem_id"]]["lane"] != "wall" for row in tasks))
        self.assertTrue(all(row["evaluation_only"] is True for row in tasks))
        self.assertTrue(all(row["frontier_id"] == f"eval_erdos_{row['problem_id']}" for row in tasks))

    def test_promotion_sample_size_matches_suite_design(self):
        evaluation = self.protocol["evaluation"]
        expected_total = (
            (evaluation["public_development_tasks"] + evaluation["private_holdout_tasks"])
            * evaluation["seeds_per_task"]
        )
        expected_holdout = evaluation["private_holdout_tasks"] * evaluation["seeds_per_task"]
        self.assertEqual(evaluation["paired_task_runs_per_candidate"], expected_total)
        self.assertEqual(self.protocol["promotion_gate"]["minimum_paired_holdout_runs"], expected_holdout)


if __name__ == "__main__":
    unittest.main()
