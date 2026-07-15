import importlib.util
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("foundry_audit", Path(__file__).parents[1] / "tools" / "foundry_audit.py")
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def row(classification, frontier="same route", result="same result", gate="same gate"):
    return {"classification": classification, "frontier": frontier, "result": result, "next_gate": gate}


class AuditTests(unittest.TestCase):
    def test_private_holdout_matches_public_commitment_without_disclosure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private"
            root.mkdir(mode=0o700)
            manifest_path = root / "private_suite.json"
            commitment_path = Path(tmp) / "commitment.json"
            manifest = {
                "schema": "p42-foundry-private-eval-suite-v1",
                "suite_version": "1.0.0", "atlas_version": "0.2.0",
                "public_suite_version": "v1", "split_salt_hex": "11" * 32,
                "tasks": [
                    {"task_id": "opaque", "problem_id": 7, "family": "exact"},
                ],
            }
            manifest_path.write_text(json.dumps(manifest)); manifest_path.chmod(0o600)
            digest = hashlib.sha256(json.dumps(
                manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode()).hexdigest()
            commitment = {
                "schema": "p42-foundry-private-suite-commitment-v1",
                "suite_version": "1.0.0", "atlas_version": "0.2.0",
                "public_suite_version": "v1", "manifest_sha256": "sha256:" + digest,
                "task_count": 1, "family_counts": {"exact": 1},
                "task_ids_or_problem_ids_disclosed": False,
            }
            commitment_path.write_text(json.dumps(commitment))
            self.assertTrue(audit.private_holdout_committed(manifest_path, commitment_path))
            commitment["problem_ids"] = [7]
            commitment_path.write_text(json.dumps(commitment))
            self.assertFalse(audit.private_holdout_committed(manifest_path, commitment_path))

    def test_model_transport_report_proves_unix_only_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "model_transport.json"
            report = {
                "schema": "p42-foundry-model-transport-v1",
                "created_at": "2026-07-15T07:00:00Z",
                "ok": True,
                "mode": "smoke",
                "candidate_network": "none",
                "model_transport": "mounted_unix_socket_only",
                "model_upstream": "evaluator_loopback_only",
                "model_upstream_host": "127.0.0.1",
                "model_upstream_port": 30000,
                "private_manifest_mounted": False,
                "docker_socket_mounted": False,
                "budget": {"budget_ok": True},
                "promotion_authority": "none_pending_independent_replay",
            }
            path.write_text(json.dumps(report)); path.chmod(0o600)
            cutoff = datetime(2026, 7, 15, 6, 0, tzinfo=timezone.utc)
            self.assertTrue(audit.model_transport_verified(report, path, cutoff))
            report["candidate_network"] = "bridge"
            self.assertFalse(audit.model_transport_verified(report, path, cutoff))

    def test_independent_replay_smoke_proves_fresh_second_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "replay.json"
            report = {
                "schema": "p42-foundry-independent-replay-v1",
                "created_at": "2026-07-15T08:00:00Z",
                "mode": "synthetic_boundary_smoke_no_rsi_claim",
                "scope": "contract_smoke",
                "ok": True,
                "verified_utility_units": 0,
                "artifact_replay_ok": True,
                "canonical_math_verdict": "pending_evaluator_owned_verifier",
                "promotion_authority": "none_smoke_only",
                "evaluator_tree_clean": True,
                "image_id": "sha256:" + "1" * 64,
                "replay_boundary": {
                    "candidate_network": "none",
                    "root_filesystem": "read_only",
                    "candidate_workspace_mounted": False,
                    "model_transport_mounted": False,
                    "private_manifest_mounted": False,
                    "docker_socket_mounted": False,
                },
                "artifact_inventory": [{"sha256": "sha256:" + "2" * 64}],
                "replays": [{"ok": True}],
            }
            path.write_text(json.dumps(report)); path.chmod(0o600)
            cutoff = datetime(2026, 7, 15, 7, 0, tzinfo=timezone.utc)
            self.assertTrue(audit.independent_replay_verified(report, path, cutoff))
            report["replay_boundary"]["model_transport_mounted"] = True
            self.assertFalse(audit.independent_replay_verified(report, path, cutoff))

    def test_paired_eval_is_operational_evidence_without_auto_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "paired.json"
            report = {
                "schema": "p42-foundry-paired-evaluation-v1",
                "created_at": "2026-07-15T08:00:00Z",
                "paired_runs": 1,
                "fixed_budget_evidence_matched": True,
                "all_replays_operational": True,
                "automatic_production_promotion": False,
                "promotion_authority": "none_human_review_required",
                "claim_status": "development_evidence_only",
            }
            path.write_text(json.dumps(report)); path.chmod(0o600)
            cutoff = datetime(2026, 7, 15, 7, 0, tzinfo=timezone.utc)
            self.assertTrue(audit.paired_evaluation_verified(report, path, cutoff))
            report["all_replays_operational"] = False
            self.assertFalse(audit.paired_evaluation_verified(report, path, cutoff))
            report["all_replays_operational"] = True
            report["automatic_production_promotion"] = True
            self.assertFalse(audit.paired_evaluation_verified(report, path, cutoff))

    def test_canonical_reward_boundary_requires_zero_self_replay_utility(self):
        protocol = {
            "schema": "p42-foundry-adjudication-protocol-v1",
            "generic_replay_utility_cap": 0,
            "paired_comparison": {
                "automatic_production_promotion": False,
                "human_review_required": True,
            },
        }
        contracts = {
            "schema": "p42-foundry-canonical-contract-registry-v1",
            "contracts": {
                key: {"verifier_id": "v" + key}
                for key in ("1", "21", "138", "552")
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            verifier = Path(tmp) / "verify.py"
            verifier.write_text("pass\n")
            self.assertTrue(
                audit.canonical_reward_boundary_locked(protocol, contracts, verifier)
            )
            protocol["generic_replay_utility_cap"] = 1
            self.assertFalse(
                audit.canonical_reward_boundary_locked(protocol, contracts, verifier)
            )

    def test_structured_quarantine_feedback_matches_rejected_hash(self):
        state = {
            "accepted": {},
            "rejected": {"job/run.md": "a" * 64},
            "rejected_details": {"job/run.md": {
                "schema": "p42-foundry-quarantine-feedback-v1",
                "source_sha256": "a" * 64,
                "errors": ["semantic contract rejected the claim"],
            }},
        }
        self.assertTrue(audit.structured_quarantine_feedback_consistent(state))
        state["rejected_details"]["job/run.md"]["source_sha256"] = "b" * 64
        self.assertFalse(audit.structured_quarantine_feedback_consistent(state))

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
