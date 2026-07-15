import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


SPEC = importlib.util.spec_from_file_location("foundry", Path(__file__).parents[1] / "tools" / "foundry.py")
foundry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(foundry)


SAMPLE = """# Cron Job: scout
**Run Time:** 2026-07-14 17:00:51
## Response
**Frontier**
Can route X move?
**Action**
Ran one bounded exact check.
**Verified**
Known-good and known-bad fixtures passed.
**Result**
No changed condition; prior verdict holds.
**Next gate**
Try route Y if its verifier exists.
**Boundary held**
No Atlas writes or submissions.
"""


class FoundryTests(unittest.TestCase):
    def test_parse_and_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-07-14_17-00-51.md"
            path.write_text(SAMPLE)
            expected_epoch = datetime(2026, 7, 15, 0, 0, 51, tzinfo=timezone.utc).timestamp()
            os.utime(path, (expected_epoch, expected_epoch))
            receipt = foundry.build_receipt(path, "50c8e4391849", "Etc/GMT+7")
            self.assertEqual(receipt["classification"], "blocked")
            self.assertEqual(receipt["occurred_at"], "2026-07-15T00:00:51Z")
            self.assertEqual(foundry.validate_receipt(receipt), [])
            self.assertTrue(receipt["receipt_id"].startswith("sha256:"))
            self.assertTrue(receipt["content_digest"].startswith("sha256:"))

    def test_required_labels_fail_closed(self):
        with self.assertRaises(ValueError):
            foundry.parse_sections("**Frontier**\nOnly one field")

    def test_classification(self):
        self.assertEqual(foundry.classify("candidate survives", "built verifier"), "progress")
        self.assertEqual(foundry.classify("local-exhaustion", "checked route"), "negative_result")
        self.assertEqual(foundry.classify("blocked by missing corpus", "audit"), "blocked")
        self.assertEqual(foundry.classify("No mathematical progress; lane remains closed", "Negative-result consolidation"), "negative_result")

    def test_ambiguous_wall_clock_falls_back_to_absolute_mtime(self):
        fallback = datetime(2026, 7, 15, 0, 0, 51, tzinfo=timezone.utc)
        self.assertEqual(foundry.parse_run_time(SAMPLE, fallback, "America/Denver"), "2026-07-15T00:00:51Z")

    def test_public_membrane_rejects_local_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-07-14_17-00-51.md"
            path.write_text(SAMPLE.replace("Known-good", "/home/chronos/private Known-good"))
            receipt = foundry.build_receipt(path, "50c8e4391849")
            self.assertIn("public membrane violation in verified", foundry.validate_receipt(receipt))

    def test_cockpit_table_fallback(self):
        text = """## Response
| Field | Value |
|---|---|
| **Lane** | `fm_hadamard_668` |
| **Status** | `control_plane_only` |
| **Changed conditions** | 0 |
| **Reproduce verifier** | 9/10 pass |
| **Action taken** | Checked source hashes |
| **Blocked** | None |
| **Next gate** | Await changed condition |
"""
        sections = foundry.parse_sections(text)
        self.assertEqual(sections["Frontier"], "`fm_hadamard_668`")
        self.assertIn("9/10 pass", sections["Verified"])

    def test_publish_retries_a_committed_but_unpushed_head(self):
        calls = []
        def fake_run(cmd, check=True):
            calls.append(cmd)
            if cmd[:3] == ["git", "status", "--short"]: return SimpleNamespace(stdout="")
            if cmd[:2] == ["git", "rev-parse"]: return SimpleNamespace(stdout="local-head\n")
            if cmd[:2] == ["git", "ls-remote"]: return SimpleNamespace(stdout="remote-head\trefs/heads/automation/frontier-scout\n")
            return SimpleNamespace(stdout="")
        with mock.patch.object(foundry, "validate"), mock.patch.object(foundry, "run", side_effect=fake_run):
            with redirect_stdout(io.StringIO()): foundry.publish("automation/frontier-scout")
        self.assertIn(["git", "push", "origin", "HEAD:automation/frontier-scout"], calls)

    def test_frontier_advice_trace_is_structured(self):
        digest = "sha256:" + "a" * 64
        sample = SAMPLE.replace(
            "Known-good and known-bad fixtures passed.",
            f"Known-good fixtures passed. Frontier advice: {digest}; executed=yes; outcome=kill-test rejected route A",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-07-14_17-00-51.md"
            path.write_text(sample)
            receipt = foundry.build_receipt(path, "50c8e4391849")
            self.assertEqual(receipt["frontier_consult"], {"advice_digest": digest, "executed": True, "outcome": "kill-test rejected route A"})
            self.assertEqual(foundry.validate_receipt(receipt), [])

    def test_pending_advice_replays_then_retires_on_executed_receipt(self):
        digest = "sha256:" + "b" * 64
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            state_path.write_text(json.dumps({
                "calls": [],
                "pending_advice": {
                    "advice": "Try the bounded parity kill-test.",
                    "advice_digest": digest,
                    "created_at": "2026-07-15T00:00:00Z",
                    "gate_receipts": [],
                    "delivery_count": 0,
                },
            }))
            first = foundry.take_pending_advice(state_path)
            self.assertEqual(first["strategy_status"], "pending")
            self.assertEqual(first["delivery_count"], 1)
            self.assertEqual(state_path.stat().st_mode & 0o777, 0o600)
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(json.dumps({
                "frontier_consult": {"advice_digest": digest, "executed": True, "outcome": "route rejected"},
            }))
            with mock.patch.object(foundry, "receipt_files", return_value=[receipt_path]):
                second = foundry.take_pending_advice(state_path)
            self.assertEqual(second["strategy_status"], "consumed")
            self.assertNotIn("pending_advice", json.loads(state_path.read_text()))


if __name__ == "__main__":
    unittest.main()
