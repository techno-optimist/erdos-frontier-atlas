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


if __name__ == "__main__":
    unittest.main()

