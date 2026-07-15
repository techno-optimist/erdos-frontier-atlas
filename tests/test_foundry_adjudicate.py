import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SPEC = importlib.util.spec_from_file_location(
    "foundry_adjudicate", Path(__file__).parents[1] / "tools" / "foundry_adjudicate.py"
)
adjudication = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adjudication)
ROOT = Path(__file__).parents[1]


class FoundryAdjudicationTests(unittest.TestCase):
    def fixture(self, root: Path):
        output = root / "candidate"
        artifacts = output / "artifacts"
        artifacts.mkdir(parents=True)
        (artifacts / "check.py").write_text("print('verified')\n")
        packet = {
            "schema": "p42-foundry-eval-task-v1",
            "evaluation_id": "opaque-task",
            "seed": 7,
            "budget": {"model": "/models/frozen"},
        }
        packet_path = root / "task.json"
        packet_path.write_text(json.dumps(packet) + "\n")
        result = {
            "schema": "p42-foundry-candidate-result-v2",
            "evaluation_id": packet["evaluation_id"],
            "seed": packet["seed"],
            "task_packet_sha256": adjudication.sha256_bytes(
                adjudication.canonical_bytes(packet)
            ),
            "classification": "progress",
            "hypothesis": "bounded",
            "falsifier": "check exits nonzero",
            "claim": "the executable artifact replays",
            "evidence": ["local fixture passed"],
            "artifacts": adjudication.artifact_inventory(artifacts),
            "artifacts_claimed": ["check.py"],
            "replay": [{"argv": ["python3", "artifacts/check.py"]}],
            "theorem_status": "theorem_unchanged",
            "independent_replay_status": "pending",
        }
        result_path = output / "result.json"
        result_path.write_text(json.dumps(result) + "\n")
        run_report = {
            "schema": "p42-foundry-model-transport-v1",
            "ok": True,
            "mode": "candidate_run",
            "budget": {"budget_ok": True, "limits": {}},
            "artifact_sha256": adjudication.sha256_file(result_path),
        }
        run_path = root / "run.json"
        run_path.write_text(json.dumps(run_report) + "\n")
        return output, packet_path, run_path

    def test_candidate_authored_replay_is_reproducible_but_zero_utility(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, packet, run = self.fixture(Path(tmp))
            replay = [{
                "index": 0,
                "argv": ["python3", "/artifacts/check.py"],
                "timeout_seconds": 180,
                "returncode": 0,
                "timed_out": False,
                "output_sha256": "sha256:" + "1" * 64,
                "output_tail": "verified",
                "ok": True,
            }]
            with mock.patch.object(adjudication, "resolve_image_id", return_value="sha256:" + "2" * 64), mock.patch.object(
                adjudication, "run_replays", return_value=replay
            ), mock.patch.object(adjudication, "_git_tree_clean", return_value=True):
                report = adjudication.adjudicate(
                    output, packet, run, "frozen-image", "private"
                )
            self.assertTrue(report["ok"])
            self.assertTrue(report["artifact_replay_ok"])
            self.assertEqual(report["verified_utility_units"], 0)
            self.assertEqual(
                report["canonical_math_verdict"],
                "pending_evaluator_owned_verifier",
            )
            self.assertFalse(report["replay_boundary"]["candidate_workspace_mounted"])
            self.assertFalse(report["replay_boundary"]["model_transport_mounted"])

    def test_evaluator_owned_hash_bound_verdict_can_award_utility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output, packet, run = self.fixture(root)
            root.chmod(0o700)
            verifier_source = root / "trusted_verifier.py"
            verifier_source.write_text("# trusted\n")
            packet_value = json.loads(packet.read_text())
            result_path = output / "result.json"
            verdict = {
                "schema": "p42-foundry-canonical-verdict-v1",
                "task_packet_sha256": adjudication.sha256_bytes(
                    adjudication.canonical_bytes(packet_value)
                ),
                "candidate_result_sha256": adjudication.sha256_file(result_path),
                "verdict": "accepted",
                "utility_units": 1,
                "independent_from_candidate": True,
                "hard_constraints_ok": True,
                "verifier_id": "fixture-verifier",
                "verifier_revision": "trusted-revision",
                "verifier_source_sha256": adjudication.sha256_file(verifier_source),
                "evidence_sha256": "sha256:" + "4" * 64,
            }
            verdict_path = root / "verdict.json"
            verdict_path.write_text(json.dumps(verdict)); verdict_path.chmod(0o600)
            replay = [{
                "index": 0, "argv": ["python3", "/artifacts/check.py"],
                "timeout_seconds": 180, "returncode": 0, "timed_out": False,
                "output_sha256": "sha256:" + "1" * 64,
                "output_tail": "verified", "ok": True,
            }]
            with mock.patch.object(adjudication, "resolve_image_id", return_value="sha256:" + "2" * 64), mock.patch.object(
                adjudication, "run_replays", return_value=replay
            ), mock.patch.object(adjudication, "_git_tree_clean", return_value=True), mock.patch.object(
                adjudication, "_git_revision", return_value="trusted-revision"
            ), mock.patch.object(adjudication, "CANONICAL_VERDICT_ROOT", root), mock.patch.dict(
                adjudication.CANONICAL_VERIFIER_SOURCES,
                {"fixture-verifier": verifier_source},
            ):
                report = adjudication.adjudicate(
                    output, packet, run, "frozen-image", "private", verdict_path
                )
            self.assertEqual(report["verified_utility_units"], 1)
            self.assertEqual(
                report["canonical_math_verdict"],
                "accepted_by_evaluator_owned_verifier",
            )
            self.assertEqual(report["canonical_verifier"]["verifier_id"], "fixture-verifier")

    def test_tampered_artifact_digest_is_zero_utility(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, packet, run = self.fixture(Path(tmp))
            result_path = output / "result.json"
            result = json.loads(result_path.read_text())
            result["artifacts"][0]["sha256"] = "sha256:" + "0" * 64
            result_path.write_text(json.dumps(result) + "\n")
            run_report = json.loads(run.read_text())
            run_report["artifact_sha256"] = adjudication.sha256_file(result_path)
            run.write_text(json.dumps(run_report) + "\n")
            report = adjudication.adjudicate(
                output, packet, run, "unused", "private", run_replay=False
            )
            self.assertFalse(report["ok"])
            self.assertEqual(report["verified_utility_units"], 0)
            self.assertIn(
                "candidate_artifact_digest_mismatch",
                report["hard_constraint_violations"],
            )

    def test_erdos_552_heuristic_nonexistence_claim_is_hard_violation(self):
        with tempfile.TemporaryDirectory() as tmp:
            output, packet, run = self.fixture(Path(tmp))
            packet_value = json.loads(packet.read_text())
            packet_value["target"] = {"id": 552}
            packet.write_text(json.dumps(packet_value))
            result_path = output / "result.json"
            result = json.loads(result_path.read_text())
            result.update({
                "classification": "negative_result",
                "hypothesis": "No C4-free graph on 22 vertices exists.",
                "claim": "Therefore R(C4,S17)=22.",
                "theorem_status": "local_result_only",
                "task_packet_sha256": adjudication.sha256_bytes(
                    adjudication.canonical_bytes(packet_value)
                ),
            })
            result_path.write_text(json.dumps(result) + "\n")
            run_value = json.loads(run.read_text())
            run_value["artifact_sha256"] = adjudication.sha256_file(result_path)
            run.write_text(json.dumps(run_value) + "\n")
            report = adjudication.adjudicate(
                output, packet, run, "unused", "public", run_replay=False
            )
            self.assertIn(
                "erdos_552_nonexistence_claim_without_replayable_proof",
                report["hard_constraint_violations"],
            )
            self.assertIn(
                "negative_result_lacks_bounded_claim_boundary",
                report["hard_constraint_violations"],
            )

    def test_bounded_negative_claim_does_not_trigger_semantic_inflation(self):
        packet = {"target": {"id": 552}}
        result = {
            "classification": "negative_result",
            "hypothesis": "bounded m=22 search",
            "claim": (
                "No witness found within this bounded search; theorem and bracket unchanged."
            ),
        }
        self.assertEqual(adjudication.semantic_contract_violations(result, packet), [])
        result["claim"] = "No witness exists within the searched universe."
        self.assertIn(
            "negative_result_lacks_bounded_claim_boundary",
            adjudication.semantic_contract_violations(result, packet),
        )

    def test_unproved_hypothesis_is_not_conflated_with_bounded_552_claim(self):
        packet = {"target": {"id": 552}}
        result = {
            "classification": "negative_result",
            "hypothesis": (
                "A witness exists and would prove R(C4,S17)>=23."
            ),
            "claim": (
                "No C4-free graph was found via this construction within the bounded budget."
            ),
            "theorem_status": "theorem_unchanged",
        }
        self.assertEqual(adjudication.semantic_contract_violations(result, packet), [])
        result["claim"] = "Therefore R(C4,S17)=22."
        self.assertIn(
            "erdos_552_nonexistence_claim_without_replayable_proof",
            adjudication.semantic_contract_violations(result, packet),
        )

    def test_replay_contract_rejects_shell_and_path_escape(self):
        inventory = [{"path": "check.py", "sha256": "sha256:x", "bytes": 1}]
        with self.assertRaisesRegex(adjudication.AdjudicationError, "frozen Python"):
            adjudication._normalized_replay_step("sh check.py", inventory)
        with self.assertRaisesRegex(adjudication.AdjudicationError, "inline or module"):
            adjudication._normalized_replay_step("python3 -c pass", inventory)
        with self.assertRaisesRegex(adjudication.AdjudicationError, "artifact path"):
            adjudication._normalized_replay_step("python3 ../check.py", inventory)

    def test_evaluator_inventory_paths_are_literal_but_legacy_claims_normalize(self):
        self.assertEqual(
            adjudication._claimed_artifact_paths({
                "artifacts": [{"path": "artifacts/check.py"}]
            }),
            {"artifacts/check.py"},
        )
        self.assertEqual(
            adjudication._claimed_artifact_paths({
                "artifacts": ["artifacts/check.py"]
            }),
            {"check.py"},
        )

    def test_replay_container_mounts_no_candidate_workspace_model_or_private_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifacts = root / "artifacts"
            artifacts.mkdir()
            task = root / "task.json"
            task.write_text("{}")
            command = adjudication.replay_sandbox_command(
                "sha256:" + "3" * 64,
                artifacts,
                task,
                {"argv": ["python3", "/artifacts/check.py"], "timeout_seconds": 1},
            )
            joined = " ".join(command)
            self.assertIn("--network none", joined)
            self.assertIn("--read-only", command)
            self.assertIn("dst=/artifacts,readonly", joined)
            self.assertIn("dst=/task/task.json,readonly", joined)
            self.assertNotIn("/workspace", joined)
            self.assertNotIn("model.sock", joined)
            self.assertNotIn("private_suite", joined)
            self.assertNotIn("docker.sock", joined)

    def test_artifact_inventory_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.py"
            target.write_text("pass\n")
            (root / "alias.py").symlink_to(target)
            with self.assertRaisesRegex(adjudication.AdjudicationError, "symlink"):
                adjudication.artifact_inventory(root)

    @staticmethod
    def report(scope, task, seed, utility, violations=None):
        return {
            "schema": "p42-foundry-independent-replay-v1",
            "scope": scope,
            "evaluation_id": task,
            "seed": seed,
            "task_packet_sha256": "sha256:" + task.zfill(64)[-64:],
            "verified_utility_units": utility,
            "hard_constraint_violations": violations or [],
            "ok": True,
            "artifact_replay_ok": True,
            "fixed_budget": {"model": "frozen", "limits": {"api_calls": 24}},
            "canonical_verifier": ({
                "verdict": "accepted",
                "independent_from_candidate": True,
                "hard_constraints_ok": True,
            } if utility else None),
        }

    def test_full_private_pair_matrix_can_only_become_human_review_candidate(self):
        protocol = json.loads((ROOT / "foundry" / "rsi_protocol.json").read_text())
        baseline = [self.report("private", str(i), i, 0) for i in range(24)]
        candidate = [self.report("private", str(i), i, 1) for i in range(24)]
        baseline.extend(self.report("public", "p" + str(i), i, 1) for i in range(12))
        candidate.extend(self.report("public", "p" + str(i), i, 1) for i in range(12))
        report = adjudication.compare_paired(
            baseline, candidate, protocol, "frozen", "candidate"
        )
        self.assertTrue(report["promotion_eligible"])
        self.assertEqual(report["private_wins"], 24)
        self.assertGreater(report["bootstrap_lower_bound"], 0)
        self.assertFalse(report["automatic_production_promotion"])
        self.assertEqual(
            report["claim_status"], "promotion_candidate_human_review_required"
        )

    def test_hard_violation_or_incomplete_matrix_cannot_promote(self):
        protocol = json.loads((ROOT / "foundry" / "rsi_protocol.json").read_text())
        baseline = [self.report("private", str(i), i, 0) for i in range(24)]
        candidate = [self.report("private", str(i), i, 1) for i in range(24)]
        candidate[0]["hard_constraint_violations"] = ["atlas_hash_drift"]
        report = adjudication.compare_paired(
            baseline, candidate, protocol, "frozen", "candidate"
        )
        self.assertFalse(report["promotion_eligible"])
        with self.assertRaisesRegex(adjudication.AdjudicationError, "incomplete"):
            adjudication.compare_paired(
                baseline, candidate[:-1], protocol, "frozen", "candidate"
            )

    def test_nonoperational_replay_cannot_promote_or_satisfy_pair_gate(self):
        protocol = json.loads((ROOT / "foundry" / "rsi_protocol.json").read_text())
        baseline = [self.report("private", str(i), i, 0) for i in range(24)]
        candidate = [self.report("private", str(i), i, 1) for i in range(24)]
        candidate[0]["artifact_replay_ok"] = False
        candidate[0]["ok"] = False
        report = adjudication.compare_paired(
            baseline, candidate, protocol, "frozen", "candidate"
        )
        self.assertFalse(report["all_replays_operational"])
        self.assertFalse(report["promotion_eligible"])

    def test_bootstrap_is_deterministic(self):
        first = adjudication.bootstrap_lower_bound([1, 0, 1, 1], seed=9)
        second = adjudication.bootstrap_lower_bound([1, 0, 1, 1], seed=9)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
