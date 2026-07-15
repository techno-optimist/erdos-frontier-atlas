import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "foundry_eval", Path(__file__).parents[1] / "tools" / "foundry_eval.py"
)
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)
ROOT = Path(__file__).parents[1]


class FoundryEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.atlas = json.loads((ROOT / "atlas" / "problems.json").read_text())
        cls.public = json.loads((ROOT / "foundry" / "eval" / "public_suite.json").read_text())
        cls.protocol = json.loads((ROOT / "foundry" / "rsi_protocol.json").read_text())
        cls.salt = "11" * 32

    def manifest(self):
        return evaluation.build_private_manifest(
            self.atlas, self.public, self.protocol, self.salt, "2026-07-15T07:00:00Z"
        )

    def test_private_split_is_deterministic_balanced_and_disjoint(self):
        first, second = self.manifest(), self.manifest()
        self.assertEqual(first, second)
        self.assertEqual(len(first["tasks"]), 12)
        self.assertEqual(
            {row["family"] for row in first["tasks"]}, set(evaluation.FAMILY_LANES)
        )
        self.assertEqual(
            {family: sum(row["family"] == family for row in first["tasks"])
             for family in evaluation.FAMILY_LANES},
            {family: 4 for family in evaluation.FAMILY_LANES},
        )
        public_ids = {row["problem_id"] for row in self.public["tasks"]}
        self.assertFalse(public_ids & {row["problem_id"] for row in first["tasks"]})

    def test_commitment_detects_manifest_tamper(self):
        manifest = self.manifest()
        commitment = evaluation.build_commitment(manifest)
        self.assertEqual(evaluation.validate_private(manifest, commitment, self.protocol), [])
        manifest["tasks"][0]["problem_id"] += 1
        self.assertIn(
            "private commitment digest mismatch",
            evaluation.validate_private(manifest, commitment, self.protocol),
        )
        manifest = self.manifest()
        bad_count = dict(evaluation.build_commitment(manifest), task_count=99)
        self.assertIn(
            "private commitment task count mismatch",
            evaluation.validate_private(manifest, bad_count, self.protocol),
        )

    def test_candidate_packet_contains_one_task_and_no_split_secret(self):
        manifest = self.manifest()
        packet = evaluation.make_task_packet(manifest["tasks"][0], self.atlas, self.protocol, 7)
        rendered = json.dumps(packet)
        self.assertEqual(packet["seed"], 7)
        self.assertEqual(packet["budget"], self.protocol["evaluation"]["budget_per_task_run"])
        self.assertNotIn(self.salt, rendered)
        self.assertNotIn("private_suite", rendered)
        self.assertEqual(packet["authority"]["promotion"], "none")

    def test_replay_ready_public_task_carries_only_its_public_canonical_contract(self):
        task = next(row for row in self.public["tasks"] if row["problem_id"] == 552)
        packet = evaluation.make_task_packet(task, self.atlas, self.protocol, 13)
        contract = packet["canonical_artifact_contract"]
        self.assertEqual(contract["verifier_id"], "erdos-552-c4-star-v1")
        self.assertEqual(contract["artifact_path"], "canonical_witness.json")
        self.assertNotIn("private", json.dumps(contract).lower())

    def test_private_atomic_state_is_mode_0600(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "private.json"
            evaluation.atomic_json(path, self.manifest(), 0o600)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_docker_sandbox_has_no_network_privilege_or_private_mount(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace, task, output = root / "workspace", root / "task.json", root / "out"
            workspace.mkdir(); output.mkdir(); task.write_text("{}")
            command = evaluation.docker_sandbox_command("alpine:3.22", workspace, task, output)
            joined = " ".join(command)
            self.assertIn("--network none", joined)
            self.assertIn("--read-only", command)
            self.assertIn("--cap-drop ALL", joined)
            self.assertIn("no-new-privileges", joined)
            self.assertNotIn("docker.sock", " ".join(arg for arg in command if "--mount" in arg))
            self.assertNotIn("private_suite", joined)

    def test_model_proxy_forces_local_model_and_enforces_budget(self):
        state = evaluation.ModelProxyState({
            "max_api_calls": 1,
            "max_input_tokens": 20_000,
            "max_output_tokens": 10,
        }, "/models/frozen-qwen")
        prepared, reservation = state.prepare({
            "model": "candidate-selected-model",
            "messages": [{"role": "user", "content": "probe"}],
            "stream": True,
            "max_tokens": 99,
        }, 100)
        self.assertEqual(prepared["model"], "/models/frozen-qwen")
        self.assertFalse(prepared["stream"])
        self.assertEqual(prepared["max_tokens"], 10)
        self.assertEqual(prepared["n"], 1)
        self.assertEqual(prepared["chat_template_kwargs"], {"enable_thinking": False})
        state.record({"usage": {"prompt_tokens": 5, "completion_tokens": 7}}, reservation)
        self.assertTrue(state.report()["budget_ok"])
        with self.assertRaises(evaluation.BudgetRejected):
            state.prepare({"messages": []}, 10)

    def test_candidate_sandbox_has_only_unix_model_transport(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            task = root / "task.json"
            output = root / "output"
            socket_dir = root / "socket"
            workspace.mkdir(); output.mkdir(); socket_dir.mkdir(); task.write_text("{}")
            command = evaluation.candidate_sandbox_command(
                "sha256:" + "1" * 64,
                workspace,
                task,
                output,
                socket_dir,
                "/models/frozen-qwen",
            )
            joined = " ".join(command)
            self.assertIn("--network none", joined)
            self.assertIn("dst=/model,readonly", joined)
            self.assertIn("FOUNDRY_MODEL_SOCKET=/model/model.sock", joined)
            self.assertNotIn("127.0.0.1", joined)
            self.assertNotIn("http://", joined)
            self.assertNotIn("docker.sock", joined)
            self.assertNotIn("private_suite", joined)
            self.assertIn("--entrypoint /usr/local/bin/python3", joined)

    def test_concurrent_requests_cannot_oversubscribe_output_budget(self):
        state = evaluation.ModelProxyState({
            "max_api_calls": 2,
            "max_input_tokens": 40_000,
            "max_output_tokens": 10,
        }, "/models/frozen-qwen")
        _, reservation = state.prepare({"messages": [], "max_tokens": 10}, 10)
        with self.assertRaises(evaluation.BudgetRejected):
            state.prepare({"messages": [], "max_tokens": 1}, 10)
        state.record({"usage": {"prompt_tokens": 2, "completion_tokens": 5}}, reservation)
        second, second_reservation = state.prepare({"messages": [], "max_tokens": 10}, 10)
        self.assertEqual(second["max_tokens"], 5)
        state.record_upstream_error(second_reservation)
        self.assertFalse(state.report()["budget_ok"])

    def test_model_sandbox_rejects_mutated_task_budget_before_docker(self):
        packet = evaluation.make_task_packet(
            self.public["tasks"][0], self.atlas, self.protocol, 11
        )
        packet["budget"]["max_api_calls"] += 1
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = root / "task.json"
            output = root / "output"
            private = root / "private.json"
            task.write_text(json.dumps(packet)); private.write_text("{}")
            with self.assertRaisesRegex(ValueError, "frozen evaluation budget"):
                evaluation.run_model_sandbox(
                    "missing-image", ROOT, task, output, private, smoke=True
                )


if __name__ == "__main__":
    unittest.main()
