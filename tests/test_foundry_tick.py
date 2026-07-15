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
    def runtime_config(self):
        return {"runtime_budget": {
            "effective_after": "2026-07-15T13:50:00Z",
            "scheduled_job_max_turns": 16,
            "max_api_calls": 16,
            "max_input_tokens": 70000,
            "max_context_growth_tokens": 45000,
            "max_wall_seconds": 900,
            "expensive_terminal_seconds": 30,
            "max_expensive_terminal_calls": 1,
            "receipt_match_window_seconds": 300,
        }}

    def runtime_receipt(self):
        return {
            "occurred_at": "2026-07-15T14:07:00Z",
            "source": {"job_id": "50c8e4391849"},
        }

    def runtime_report(self, config, **overrides):
        session = {
            "session_id": "cron_50c8e4391849_20260715_065247",
            "job_id": "50c8e4391849", "status": "complete",
            "ended_at": "2026-07-15T14:06:58Z", "api_call_count": 12,
            "max_input_tokens": 60000, "context_growth_tokens": 38000,
            "wall_seconds": 700, "token_accounting_consistent": True,
            "expensive_terminal_calls": [{"duration_seconds": 80.0}],
        }
        session.update(overrides)
        return {
            "runtime_budget_digest": foundry_tick.runtime_budget_digest(config),
            "telemetry_contract_digest": foundry_tick.telemetry_contract_digest(config),
            "sessions": [session],
        }

    def test_runtime_budget_accepts_hash_time_bound_session(self):
        config = self.runtime_config()
        errors, evidence = foundry_tick.runtime_budget_assessment(
            self.runtime_receipt(), self.runtime_report(config), config
        )
        self.assertEqual(errors, [])
        self.assertEqual(evidence["status"], "within_budget")
        self.assertEqual(evidence["source_end_delta_seconds"], 2)

    def test_runtime_budget_uses_operator_bound_job_for_raw_draft(self):
        config = self.runtime_config()
        receipt = {"occurred_at": "2026-07-15T14:07:00Z"}
        errors, evidence = foundry_tick.runtime_budget_assessment(
            receipt,
            self.runtime_report(config),
            config,
            source_job_id="50c8e4391849",
        )
        self.assertEqual(errors, [])
        self.assertEqual(evidence["session_id"], "cron_50c8e4391849_20260715_065247")

    def test_runtime_budget_rejects_observed_runaway_loop(self):
        config = self.runtime_config()
        report = self.runtime_report(
            config, api_call_count=24, max_input_tokens=92000,
            context_growth_tokens=70000, wall_seconds=960,
            expensive_terminal_calls=[
                {"duration_seconds": 97.93}, {"duration_seconds": 60.07},
            ],
        )
        errors, evidence = foundry_tick.runtime_budget_assessment(
            self.runtime_receipt(), report, config
        )
        self.assertEqual(len(errors), 5)
        self.assertEqual(evidence["status"], "over_budget")
        self.assertEqual(evidence["observed"]["expensive_terminal_call_count"], 2)

    def test_runtime_budget_fails_closed_without_matching_telemetry(self):
        config = self.runtime_config()
        errors, evidence = foundry_tick.runtime_budget_assessment(
            self.runtime_receipt(), None, config
        )
        self.assertIn("telemetry unavailable", errors[0])
        self.assertIsNone(evidence)

    def test_runtime_budget_fails_closed_on_parser_contract_mismatch(self):
        config = self.runtime_config()
        report = self.runtime_report(config)
        report["telemetry_contract_digest"] = "sha256:" + "0" * 64
        errors, evidence = foundry_tick.runtime_budget_assessment(
            self.runtime_receipt(), report, config
        )
        self.assertIn("parser contract", errors[0])
        self.assertEqual(evidence["status"], "telemetry_contract_mismatch")

    def test_parser_change_invalidates_publication_policy_digest(self):
        config = self.runtime_config()
        with tempfile.TemporaryDirectory() as tmp:
            parser = Path(tmp) / "parser.py"
            parser.write_text("v1\n")
            with mock.patch.object(foundry_tick, "EFFICIENCY_PARSER", parser):
                first = foundry_tick.semantic_contract_digest(config)
                parser.write_text("v2\n")
                second = foundry_tick.semantic_contract_digest(config)
        self.assertNotEqual(first, second)

    def test_milestone_policy_change_invalidates_publication_policy_digest(self):
        config = self.runtime_config()
        config["milestone_policy"] = {"receipt_deadline_call": 14}
        first = foundry_tick.semantic_contract_digest(config)
        config["milestone_policy"]["receipt_deadline_call"] = 13
        second = foundry_tick.semantic_contract_digest(config)
        self.assertNotEqual(first, second)

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
        contract_digest = "sha256:" + "c" * 64
        detail = foundry_tick.rejection_detail(
            inspection, "fallback", contract_digest
        )
        self.assertEqual(detail["schema"], "p42-foundry-quarantine-feedback-v1")
        self.assertEqual(detail["frontier_id"], "erdos_1029_r55")
        self.assertEqual(detail["source_sha256"], "a" * 64)
        self.assertEqual(detail["semantic_contract_digest"], contract_digest)
        self.assertNotIn("run_file", detail)

    def test_rejection_detail_preserves_runtime_evidence(self):
        inspection = {
            "source_sha256": "a" * 64, "receipt": {},
            "errors": ["runtime budget exceeded"],
            "runtime_telemetry": {"status": "over_budget", "session_id": "s"},
        }
        detail = foundry_tick.rejection_detail(inspection, "fallback")
        self.assertEqual(detail["runtime_telemetry"]["session_id"], "s")
        self.assertIn("shrink the action", detail["remediation"])
        self.assertIn("says nothing", detail["remediation"])

    def test_rejection_feedback_is_replayed_after_contract_change(self):
        source_sha = "a" * 64
        old_digest = "sha256:" + "b" * 64
        new_digest = "sha256:" + "c" * 64
        detail = {
            "source_sha256": source_sha,
            "semantic_contract_digest": old_digest,
        }
        self.assertTrue(
            foundry_tick.rejection_feedback_is_current(
                detail, source_sha, old_digest
            )
        )
        self.assertFalse(
            foundry_tick.rejection_feedback_is_current(
                detail, source_sha, new_digest
            )
        )

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
