import importlib.util
import tempfile
import unittest
from pathlib import Path


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
            receipt = foundry.build_receipt(path, "50c8e4391849")
            self.assertEqual(receipt["classification"], "blocked")
            self.assertEqual(receipt["occurred_at"], "2026-07-14T23:00:51Z")
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


if __name__ == "__main__":
    unittest.main()
