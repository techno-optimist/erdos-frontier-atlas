import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("foundry_tick", ROOT / "tools" / "foundry_tick.py")
foundry_tick = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(foundry_tick)


class FoundryTickTests(unittest.TestCase):
    def test_exact_accepted_or_rejected_hash_is_skipped(self):
        state = {
            "accepted": {"job/accepted.md": "aaa"},
            "rejected": {"job/rejected.md": "bbb"},
        }
        self.assertTrue(foundry_tick.source_is_watermarked(state, "job/accepted.md", "aaa"))
        self.assertTrue(foundry_tick.source_is_watermarked(state, "job/rejected.md", "bbb"))

    def test_changed_or_unseen_source_is_reprocessed(self):
        state = {"accepted": {"job/run.md": "old"}, "rejected": {}}
        self.assertFalse(foundry_tick.source_is_watermarked(state, "job/run.md", "new"))
        self.assertFalse(foundry_tick.source_is_watermarked(state, "job/unseen.md", "new"))

    def test_rejection_detail_is_bounded_structured_feedback(self):
        inspection = {
            "source_sha256": "a" * 64,
            "receipt": {
                "receipt_id": "sha256:" + "b" * 64,
                "frontier_id": "erdos_1029_r55",
                "classification": "negative_result",
                "occurred_at": "2026-07-15T07:27:23Z",
            },
            "errors": ["semantic contract quantity-conflation claim: cyclic exhausted"],
        }
        detail = foundry_tick.rejection_detail(inspection, "fallback")
        self.assertEqual(detail["schema"], "p42-foundry-quarantine-feedback-v1")
        self.assertEqual(detail["frontier_id"], "erdos_1029_r55")
        self.assertEqual(detail["source_sha256"], "a" * 64)
        self.assertNotIn("run_file", detail)

    def test_legacy_hash_only_quarantine_can_be_tombstoned(self):
        detail = foundry_tick.rejection_detail({
            "source_sha256": "c" * 64,
            "receipt": None,
            "errors": ["legacy raw source unavailable; hash-only quarantine retained"],
        }, "fallback")
        self.assertEqual(detail["source_sha256"], "c" * 64)
        self.assertIsNone(detail["frontier_id"])
        self.assertIn("unavailable", detail["errors"][0])

    def test_failed_accepted_source_is_quarantined_and_receipt_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job_id = "50c8e4391849"
            source_dir = root / "cron" / job_id
            source_dir.mkdir(parents=True)
            source = source_dir / "failed.md"
            source.write_text("# Cron Job: scout (FAILED)\n## Error\nconnection\n")
            source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
            receipt_dir = root / "repo" / "progress" / "receipts" / "2026" / "07"
            receipt_dir.mkdir(parents=True)
            receipt_path = receipt_dir / "bad.json"
            receipt_path.write_text(json.dumps({
                "source": {"job_id": job_id, "run_file": source.name, "sha256": source_sha}
            }))
            state = {
                "accepted": {f"{job_id}/{source.name}": source_sha},
                "rejected": {}, "rejected_details": {},
            }
            inspection = {
                "source_sha256": source_sha, "receipt": None,
                "errors": ["failed cron run is not a mathematical receipt"],
            }
            with mock.patch.object(foundry_tick, "inspect_run", return_value=inspection):
                revoked = foundry_tick.quarantine_invalid_accepted_sources(
                    state, root / "cron", root / "repo", root / "tool.py"
                )
            self.assertEqual(len(revoked), 1)
            self.assertFalse(receipt_path.exists())
            self.assertNotIn(f"{job_id}/{source.name}", state["accepted"])
            self.assertEqual(state["rejected"][f"{job_id}/{source.name}"], source_sha)

    def test_template_receipt_is_quarantined_after_raw_source_rotation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job_id = "50c8e4391849"
            source_sha = "a" * 64
            run_file = "rotated-away.md"
            receipt_dir = root / "repo" / "progress" / "receipts" / "2026" / "07"
            receipt_dir.mkdir(parents=True)
            receipt_path = receipt_dir / "bad.json"
            receipt_path.write_text(json.dumps({
                "receipt_id": "sha256:" + "b" * 64,
                "frontier": "<one public-safe question/anchor>",
                "source": {"job_id": job_id, "run_file": run_file, "sha256": source_sha},
            }))
            state = {
                "accepted": {f"{job_id}/{run_file}": source_sha},
                "rejected": {}, "rejected_details": {},
            }
            revoked = foundry_tick.quarantine_invalid_accepted_sources(
                state, root / "cron", root / "repo", root / "tool.py"
            )
            self.assertEqual(len(revoked), 1)
            self.assertFalse(receipt_path.exists())
            detail = state["rejected_details"][f"{job_id}/{run_file}"]
            self.assertIn("raw source unavailable", detail["errors"][0])

    def test_legacy_template_receipt_without_ingest_row_is_quarantined(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job_id = "50c8e4391849"
            source_sha = "c" * 64
            run_file = "pre-ledger.md"
            receipt_dir = root / "repo" / "progress" / "receipts" / "2026" / "07"
            receipt_dir.mkdir(parents=True)
            receipt_path = receipt_dir / "legacy.json"
            receipt_path.write_text(json.dumps({
                "receipt_id": "sha256:" + "d" * 64,
                "frontier": "<one public-safe question/anchor>",
                "source": {"job_id": job_id, "run_file": run_file, "sha256": source_sha},
            }))
            state = {"accepted": {}, "rejected": {}, "rejected_details": {}}
            revoked = foundry_tick.quarantine_invalid_accepted_sources(
                state, root / "cron", root / "repo", root / "tool.py"
            )
            self.assertEqual(len(revoked), 1)
            self.assertFalse(receipt_path.exists())
            self.assertEqual(state["rejected"][f"{job_id}/{run_file}"], source_sha)
            self.assertIn(
                "legacy private acceptance",
                state["rejected_details"][f"{job_id}/{run_file}"]["errors"][0],
            )


if __name__ == "__main__":
    unittest.main()
