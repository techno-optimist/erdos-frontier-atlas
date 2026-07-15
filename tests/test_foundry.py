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
ROOT = Path(__file__).parents[1]


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

    def test_failed_cron_prompt_template_cannot_become_a_receipt(self):
        failed = """# Cron Job: scout (FAILED)
## Prompt
**Frontier**
<one public-safe question/anchor>
## Error
RuntimeError: Connection error.
"""
        with self.assertRaisesRegex(ValueError, "failed cron run"):
            foundry.parse_sections(failed)

    def test_public_template_placeholder_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.md"
            path.write_text(SAMPLE.replace("Can route X move?", "<frontier placeholder>"))
            receipt = foundry.build_receipt(path, "50c8e4391849")
        self.assertIn("template placeholder in frontier", foundry.validate_receipt(receipt))

    def test_inspection_returns_structured_semantic_rejection_without_writing(self):
        sample = (
            '{"frontier_id":"erdos_1029_r55"}\n'
            + SAMPLE.replace(
                "Ran one bounded exact check.",
                "Ran a K5 and independent-set verifier over 4,000 random samples.",
            ).replace(
                "No changed condition; prior verdict holds.",
                "The circulant approach is exhausted and infeasible.",
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.md"
            path.write_text(sample)
            result = foundry.inspect_source(
                path, "50c8e4391849",
                json.loads((ROOT / "foundry" / "config.json").read_text()),
            )
        self.assertFalse(result["valid"])
        self.assertEqual(result["receipt"]["frontier_id"], "erdos_1029_r55")
        self.assertTrue(any("quantity-conflation" in row for row in result["errors"]))

    def test_system_postamble_is_outside_six_field_membrane(self):
        sample = SAMPLE + "\n---\n\nObservation outside receipt.\n⚠️ File-mutation verifier: /home/private/path\n"
        sections = foundry.parse_sections(sample)
        self.assertEqual(sections["Boundary held"], "No Atlas writes or submissions.")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.md"
            path.write_text(sample)
            receipt = foundry.build_receipt(path, "50c8e4391849")
            self.assertEqual(foundry.validate_receipt(receipt), [])

    def test_strategy_digest_requires_exact_typed_verified_trace(self):
        digest = "sha256:" + "a" * 64
        sample = '{"foundry":{"strategy_digest":"' + digest + '"}}\n' + SAMPLE
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.md"
            path.write_text(sample)
            receipt = foundry.build_receipt(path, "50c8e4391849")
            errors = foundry.required_strategy_trace_errors(sample, receipt)
            self.assertTrue(any("missing required typed frontier trace" in row for row in errors))

            traced = sample.replace(
                "Known-good and known-bad fixtures passed.",
                "Known-good and known-bad fixtures passed.\n"
                f"Frontier advice: {digest}; executed=yes; outcome=parameter test rejected route",
            )
            path.write_text(traced)
            receipt = foundry.build_receipt(path, "50c8e4391849")
            self.assertEqual(foundry.required_strategy_trace_errors(traced, receipt), [])
            self.assertTrue(receipt["frontier_consult"]["executed"])

    def test_strategy_trace_digest_mismatch_is_rejected(self):
        required = "sha256:" + "b" * 64
        actual = "sha256:" + "c" * 64
        sample = '{"strategy_digest":"' + required + '"}\n' + SAMPLE.replace(
            "Known-good and known-bad fixtures passed.",
            f"Frontier advice: {actual}; executed=no; outcome=blocked",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.md"
            path.write_text(sample)
            receipt = foundry.build_receipt(path, "50c8e4391849")
        self.assertTrue(any(
            "digest mismatch" in row
            for row in foundry.required_strategy_trace_errors(sample, receipt)
        ))

    def test_classification(self):
        self.assertEqual(foundry.classify("candidate survives", "built verifier"), "progress")
        self.assertEqual(foundry.classify("local-exhaustion", "checked route"), "negative_result")
        self.assertEqual(foundry.classify("blocked by missing corpus", "audit"), "blocked")
        self.assertEqual(foundry.classify("No mathematical progress; lane remains closed", "Negative-result consolidation"), "negative_result")
        self.assertEqual(
            foundry.classify(
                "Inconclusive — no witness found in the bounded sample; the bracket is unchanged.",
                "Built a verifier and ran 8,000 seeds.",
            ),
            "negative_result",
        )

    def test_ambiguous_wall_clock_falls_back_to_absolute_mtime(self):
        fallback = datetime(2026, 7, 15, 0, 0, 51, tzinfo=timezone.utc)
        self.assertEqual(foundry.parse_run_time(SAMPLE, fallback, "America/Denver"), "2026-07-15T00:00:51Z")

    def test_public_membrane_rejects_local_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-07-14_17-00-51.md"
            path.write_text(SAMPLE.replace("Known-good", "/home/chronos/private Known-good"))
            receipt = foundry.build_receipt(path, "50c8e4391849")
            self.assertIn("public membrane violation in verified", foundry.validate_receipt(receipt))

    def test_semantic_contract_rejects_quantity_substitution(self):
        receipt = {
            "frontier_id": "fm_stretched_lr", "occurred_at": "2026-07-15T04:54:56Z",
            "frontier": "Are stretched LR coefficients always non-negative?",
            "action": "Evaluated LR values for t=1 through 8.",
            "verified": "All evaluated values were non-negative.",
            "result": "All stretched LR coefficients are non-negative. This confirms the Knutson-Tao saturation theorem.",
            "next_gate": "Close the route.",
        }
        config = {
            "semantic_contracts": {"fm_stretched_lr": {
                "effective_after": "2026-07-15T04:40:00Z",
                "target_quantity": "polynomial coefficient signs, not evaluated values",
                "required_evidence_any": ["polynomial coefficient", "interpolation coefficients"],
                "forbidden_claim_patterns": ["all stretched (littlewood[- ]richardson|lr) coefficients are non-negative"],
            }}
        }
        errors = foundry.semantic_contract_errors(receipt, config)
        self.assertTrue(any("missing target-quantity evidence" in error for error in errors))
        self.assertTrue(any("quantity-conflation" in error for error in errors))

    def test_semantic_contract_scans_verified_claims_for_substitution(self):
        receipt = {
            "frontier_id": "arena_scorer_hardening",
            "occurred_at": "2026-07-15T06:41:36Z",
            "frontier": "Are live scorers aligned?",
            "action": "Executed verifier parity and PNT liveness checks.",
            "verified": "Zero difference on all 4 reachable problems.",
            "result": "Negative-result closure.",
            "next_gate": "Rotate.",
        }
        config = {
            "semantic_contracts": {
                "arena_scorer_hardening": {
                    "effective_after": "2026-07-15T06:30:00Z",
                    "target_quantity": "exact numerical comparison versus liveness",
                    "required_evidence_any": ["verifier parity", "pnt"],
                    "forbidden_claim_patterns": [
                        "zero (difference|diff).{0,80}all (4|four)"
                    ],
                }
            }
        }
        errors = foundry.semantic_contract_errors(receipt, config)
        self.assertTrue(any("quantity-conflation" in error for error in errors))

    def test_semantic_contract_accepts_exact_target_evidence(self):
        receipt = {
            "frontier_id": "fm_stretched_lr", "occurred_at": "2026-07-15T05:00:00Z",
            "frontier": "Can a stretching polynomial have a negative coefficient?",
            "action": "Computed interpolation coefficients with a held-out value check.",
            "verified": "Polynomial coefficient vector reproduced exactly.",
            "result": "No negative polynomial coefficient in this bounded row.",
            "next_gate": "Try a changed generator.",
        }
        config = {"semantic_contracts": {"fm_stretched_lr": {
            "effective_after": "2026-07-15T04:40:00Z", "target_quantity": "polynomial coefficients",
            "required_evidence_any": ["polynomial coefficient", "interpolation coefficients"],
            "forbidden_claim_patterns": ["all stretched (littlewood[- ]richardson|lr) coefficients are non-negative"],
        }}}
        self.assertEqual(foundry.semantic_contract_errors(receipt, config), [])

    def test_r55_contract_rejects_exhaustion_from_random_sampling(self):
        receipt = {
            "frontier_id": "erdos_1029_r55", "occurred_at": "2026-07-15T07:27:00Z",
            "frontier": "Can random circulant sampling move the finite R(5,5) bracket?",
            "action": "Ran a K5 and independent-set verifier over 4,000 samples.",
            "verified": "Every sampled graph contained a 5-clique in one color.",
            "result": "The circulant approach is exhausted and infeasible.",
            "next_gate": "Close the route.",
        }
        config = json.loads((ROOT / "foundry" / "config.json").read_text())
        errors = foundry.semantic_contract_errors(receipt, config)
        self.assertTrue(any("quantity-conflation" in error for error in errors))

    def test_r55_contract_accepts_bounded_negative_sample(self):
        receipt = {
            "frontier_id": "erdos_1029_r55", "occurred_at": "2026-07-15T07:27:00Z",
            "frontier": "Can random circulant sampling move the finite R(5,5) bracket?",
            "action": "Ran a K5 and independent-set verifier over 4,000 samples.",
            "verified": "Every sampled graph contained a 5-clique in one color.",
            "result": "No witness was found in this bounded random sample; the bracket is unchanged.",
            "next_gate": "Use a structurally changed generator or rotate.",
        }
        config = json.loads((ROOT / "foundry" / "config.json").read_text())
        self.assertEqual(foundry.semantic_contract_errors(receipt, config), [])

    def test_c4_star_contract_rejects_off_by_one_equivalence_and_impossible_gate(self):
        receipt = {
            "frontier_id": "erdos_552_c4_star_n17",
            "occurred_at": "2026-07-15T08:09:19Z",
            "frontier": "Does a C4-free graph on 22 vertices with minimum degree 5 exist? Equivalent: R(C4, S₁₇) ≥ 22.",
            "action": "Ran an exact codegree and minimum degree verifier.",
            "verified": "No witness in 8,000 bounded seeds; codegree checks passed on fixtures.",
            "result": "No witness was found; the bracket is unchanged.",
            "next_gate": "Try a C4-free bipartite graph on (11,11) with min_degree ≥ 5.",
        }
        config = json.loads((ROOT / "foundry" / "config.json").read_text())
        errors = foundry.semantic_contract_errors(receipt, config)
        self.assertEqual(sum("quantity-conflation" in error for error in errors), 2)

    def test_c4_star_contract_accepts_bounded_result_and_correct_target(self):
        receipt = {
            "frontier_id": "erdos_552_c4_star_n17",
            "occurred_at": "2026-07-15T08:09:19Z",
            "frontier": "Can a 22-vertex C4-free graph of minimum degree 5 prove R(C4,S17) ≥ 23?",
            "action": "Ran an exact codegree and minimum degree verifier.",
            "verified": "No witness in 8,000 bounded seeds; codegree checks passed on fixtures.",
            "result": "No witness was found in the bounded sample; the bracket remains 22..23.",
            "next_gate": "Use degree-sequence SAT with a replayable certificate or rotate.",
        }
        config = json.loads((ROOT / "foundry" / "config.json").read_text())
        self.assertEqual(foundry.semantic_contract_errors(receipt, config), [])

    def test_r3_212_contract_rejects_heuristic_support_for_exact_value(self):
        receipt = {
            "frontier_id": "erdos_140_r3_212",
            "occurred_at": "2026-07-15T08:55:37Z",
            "frontier": "Can a 44-element 3-AP-free subset of [1,212] be found?",
            "action": "Ran a 3-AP verifier and bounded random search.",
            "verified": "No 44-set was found; r_3(212) search was incomplete.",
            "result": (
                "The heuristic search supports r_3(212) = 43, but cannot certify it."
            ),
            "next_gate": "Obtain complete proof-producing nonexistence shards.",
        }
        config = json.loads((ROOT / "foundry" / "config.json").read_text())
        errors = foundry.semantic_contract_errors(receipt, config)
        self.assertTrue(any("quantity-conflation" in error for error in errors))

    def test_r3_212_contract_accepts_bounded_no_witness_result(self):
        receipt = {
            "frontier_id": "erdos_140_r3_212",
            "occurred_at": "2026-07-15T08:55:37Z",
            "frontier": "Can a 44-element 3-AP-free subset of [1,212] be found?",
            "action": "Ran a 3-AP verifier and bounded random search.",
            "verified": "No 44-set was found; r_3(212) search was incomplete.",
            "result": "No witness was found in the bounded search; bracket unchanged.",
            "next_gate": "Use a changed exact search or complete certificate.",
        }
        config = json.loads((ROOT / "foundry" / "config.json").read_text())
        self.assertEqual(foundry.semantic_contract_errors(receipt, config), [])

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

    def test_script_output_frontier_id_is_structured(self):
        sample = SAMPLE.replace("## Response", '"frontier_id": "fm_steiner_large"\n## Response')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.md"
            path.write_text(sample)
            receipt = foundry.build_receipt(path, "50c8e4391849")
            self.assertEqual(receipt["frontier_id"], "fm_steiner_large")
            self.assertEqual(foundry.validate_receipt(receipt), [])

    def test_lane_scoped_gate_ignores_other_frontier_stalls(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for index, frontier_id in enumerate(("lane_a", "lane_a")):
                path = Path(tmp) / f"{index}.json"
                path.write_text(json.dumps({
                    "receipt_id": f"sha256:{index:064x}", "frontier_id": frontier_id,
                    "frontier": "same", "classification": "blocked",
                    "result": "same closure", "next_gate": "same gate",
                }))
                paths.append(path)
            state = Path(tmp) / "state.json"
            state.write_text('{"calls": []}')
            config = {"stall_window": 3, "stall_threshold": 2, "frontier_cooldown_minutes": 360, "frontier_calls_per_utc_day": 2}
            with mock.patch.object(foundry, "receipt_files", return_value=paths):
                self.assertTrue(foundry.stall_gate(state, config, "lane_a")["stuck"])
                self.assertFalse(foundry.stall_gate(state, config, "lane_b")["stuck"])

    def test_pending_advice_replays_then_retires_on_executed_receipt(self):
        digest = "sha256:" + "b" * 64
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            state_path.write_text(json.dumps({
                "calls": [],
                "pending_advice": {
                    "advice": "Try the bounded parity kill-test.",
                    "advice_digest": digest,
                    "frontier_id": "fm_test",
                    "created_at": "2026-07-15T00:00:00Z",
                    "gate_receipts": [],
                    "delivery_count": 0,
                },
            }))
            first = foundry.take_pending_advice(state_path, "fm_test")
            self.assertEqual(first["strategy_status"], "pending")
            self.assertEqual(first["delivery_count"], 1)
            self.assertEqual(state_path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(foundry.take_pending_advice(state_path, "fm_other")["strategy_status"], "pinned_elsewhere")
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(json.dumps({
                "frontier_consult": {"advice_digest": digest, "executed": True, "outcome": "route rejected"},
            }))
            with mock.patch.object(foundry, "receipt_files", return_value=[receipt_path]):
                second = foundry.take_pending_advice(state_path, "fm_test")
            self.assertEqual(second["strategy_status"], "consumed")
            self.assertNotIn("pending_advice", json.loads(state_path.read_text()))

    def test_consult_uses_private_cross_job_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "budget.json"
            state.write_text('{"calls": []}')
            with mock.patch.object(foundry, "_consult_locked", return_value="advice") as inner:
                self.assertEqual(foundry.consult("question", state, {}, "lane"), "advice")
            inner.assert_called_once_with("question", state, {}, "lane")
            lock = state.with_suffix(state.suffix + ".consult.lock")
            self.assertTrue(lock.exists())
            self.assertEqual(lock.stat().st_mode & 0o777, 0o600)

    def test_acknowledged_cross_frontier_call_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(json.dumps({"receipt_id": "sha256:" + "c" * 64, "frontier_id": "certified_lane"}))
            state_path = Path(tmp) / "state.json"
            state_path.write_text(json.dumps({"calls": [{
                "answer_sha256": "d" * 64, "gate_receipts": ["sha256:" + "c" * 64],
            }]}))
            with mock.patch.object(foundry, "receipt_files", return_value=[receipt_path]):
                incident = foundry.acknowledge_call_incident(state_path, "d" * 64, "consulted_lane")
            self.assertEqual(incident["kind"], "cross_frontier_global_gate")
            self.assertEqual(incident["gate_receipt_frontier_ids"], ["certified_lane"])


if __name__ == "__main__":
    unittest.main()
