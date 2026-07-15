import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("foundry_audit", Path(__file__).parents[1] / "tools" / "foundry_audit.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def row(classification, frontier="same route", result="same result", gate="same gate"):
    return {"classification": classification, "frontier": frontier, "result": result, "next_gate": gate}


class AuditTests(unittest.TestCase):
    def test_repeated_terminal_route_is_certified_stall(self):
        self.assertTrue(audit.certified_stall([row("negative_result"), row("blocked")], 2))

    def test_progress_breaks_terminal_stall_chain(self):
        self.assertFalse(audit.certified_stall([row("blocked"), row("blocked"), row("progress")], 2))

    def test_different_terminal_routes_are_not_stuck(self):
        a = row("blocked", "alpha topology", "alpha failure", "alpha falsifier")
        b = row("negative_result", "zeta geometry", "zeta closure", "zeta certificate")
        self.assertFalse(audit.certified_stall([a, b], 2))

    def test_structured_frontier_id_certifies_reworded_same_lane(self):
        a = row("blocked", "one phrasing", "first closure", "first gate")
        b = row("negative_result", "unrelated wording", "second closure", "second gate")
        a["frontier_id"] = b["frontier_id"] = "fm_steiner_large"
        self.assertTrue(audit.certified_stall([a, b], 2))

    def test_public_quarantine_matches_private_rejection_and_no_receipt(self):
        source_sha = "a" * 64
        incidents = [{
            "schema": "p42-foundry-publication-incident-v1",
            "status": "quarantined_before_publication", "source_sha256": source_sha,
        }]
        state = {"rejected": {"job/run.md": source_sha}}
        self.assertTrue(audit.publication_quarantines_consistent([], incidents, state))
        self.assertFalse(audit.publication_quarantines_consistent(
            [{"source": {"sha256": source_sha}}], incidents, state,
        ))

    def test_missing_public_quarantine_is_not_proof(self):
        self.assertFalse(audit.publication_quarantines_consistent([], [], {"rejected": {}}))


if __name__ == "__main__":
    unittest.main()
