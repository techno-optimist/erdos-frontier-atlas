import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SPEC = importlib.util.spec_from_file_location(
    "foundry_candidate_worker",
    Path(__file__).parents[1] / "tools" / "foundry_candidate_worker.py",
)
worker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(worker)


class CandidateWorkerTests(unittest.TestCase):
    def test_workspace_reader_rejects_host_paths(self):
        with self.assertRaises(ValueError):
            worker._workspace_path("/etc/passwd")
        with self.assertRaises(ValueError):
            worker._workspace_path("../../private_suite.json")

    def test_artifact_writer_rejects_output_escape(self):
        with self.assertRaises(ValueError):
            worker._artifact_path("../result.json")
        with self.assertRaises(ValueError):
            worker._artifact_path("/tmp/result.json")

    def test_artifact_writer_normalizes_one_common_root_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "output"
            with mock.patch.object(worker, "OUTPUT", output):
                expected = output / "artifacts" / "check.py"
                self.assertEqual(worker._artifact_path("check.py"), expected)
                self.assertEqual(worker._artifact_path("artifacts/check.py"), expected)
                self.assertEqual(
                    worker._artifact_path("/output/artifacts/check.py"), expected
                )
                with self.assertRaises(ValueError):
                    worker._artifact_path("artifacts/artifacts/check.py")

    def test_tool_contract_requires_typed_submission(self):
        submit = next(row for row in worker.TOOLS if row["function"]["name"] == "submit_result")
        required = set(submit["function"]["parameters"]["required"])
        self.assertTrue({"hypothesis", "falsifier", "evidence", "replay", "theorem_status"} <= required)
        theorem = submit["function"]["parameters"]["properties"]["theorem_status"]
        self.assertEqual(
            set(theorem["enum"]),
            {"witness_only", "local_result_only", "certificate_pending", "theorem_unchanged"},
        )

    def test_submission_is_bound_and_content_addressed_by_worker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "output"
            task_path = root / "task.json"
            (output / "artifacts").mkdir(parents=True)
            (output / "artifacts" / "check.py").write_text("print('ok')\n")
            (output / "artifacts" / "scratch.py").write_text("raise SystemExit(9)\n")
            task = {"evaluation_id": "opaque", "seed": 9}
            task_path.write_text(json.dumps(task))
            payload = {
                "classification": "progress",
                "hypothesis": "h",
                "falsifier": "f",
                "claim": "c",
                "evidence": ["e"],
                "artifacts": ["artifacts/check.py"],
                "replay": [{"argv": ["python3", "artifacts/check.py"]}],
                "theorem_status": "theorem_unchanged",
            }
            with mock.patch.object(worker, "OUTPUT", output), mock.patch.object(
                worker, "TASK_PATH", task_path
            ):
                response = json.loads(worker.execute_tool("submit_result", payload))
            self.assertTrue(response["submitted"])
            result = json.loads((output / "result.json").read_text())
            self.assertEqual(result["schema"], "p42-foundry-candidate-result-v2")
            self.assertEqual(result["evaluation_id"], "opaque")
            self.assertEqual(result["seed"], 9)
            self.assertEqual(result["artifacts"][0]["path"], "check.py")
            self.assertTrue(result["artifacts"][0]["sha256"].startswith("sha256:"))
            self.assertFalse((output / "artifacts" / "scratch.py").exists())
            self.assertEqual(result["artifacts_claimed"], ["check.py"])

    def test_prefixed_write_is_inventory_normalized(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "output"
            output.mkdir()
            with mock.patch.object(worker, "OUTPUT", output):
                response = json.loads(worker.execute_tool(
                    "write_artifact",
                    {"path": "artifacts/check.py", "content": "pass\n"},
                ))
                self.assertEqual(response["written"], "artifacts/check.py")
                self.assertEqual(worker._artifact_inventory()[0]["path"], "check.py")

    def test_submission_returns_failed_replay_for_correction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "output"
            task_path = root / "task.json"
            (output / "artifacts").mkdir(parents=True)
            (output / "artifacts" / "bad.py").write_text("raise SystemExit(7)\n")
            task_path.write_text(json.dumps({"evaluation_id": "opaque", "seed": 9}))
            payload = {
                "classification": "progress",
                "hypothesis": "h",
                "falsifier": "f",
                "claim": "c",
                "evidence": ["e"],
                "artifacts": ["bad.py"],
                "replay": [{"argv": ["python3", "bad.py"]}],
                "theorem_status": "theorem_unchanged",
            }
            with mock.patch.object(worker, "OUTPUT", output), mock.patch.object(
                worker, "TASK_PATH", task_path
            ):
                response = json.loads(worker.execute_tool("submit_result", payload))
            self.assertEqual(response["error"], "ValueError")
            self.assertIn("candidate replay preflight failed", response["message"])
            self.assertFalse((output / "result.json").exists())

    def test_submission_requires_replay_for_every_final_python_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "output"
            task_path = root / "task.json"
            (output / "artifacts").mkdir(parents=True)
            (output / "artifacts" / "check.py").write_text("print('ok')\n")
            task_path.write_text(json.dumps({"evaluation_id": "opaque", "seed": 9}))
            payload = {
                "classification": "progress",
                "hypothesis": "h",
                "falsifier": "f",
                "claim": "c",
                "evidence": ["e"],
                "artifacts": ["check.py"],
                "replay": [],
                "theorem_status": "theorem_unchanged",
            }
            with mock.patch.object(worker, "OUTPUT", output), mock.patch.object(
                worker, "TASK_PATH", task_path
            ):
                response = json.loads(worker.execute_tool("submit_result", payload))
            self.assertEqual(response["error"], "ValueError")
            self.assertIn(
                "every final Python artifact requires replay", response["message"]
            )
            self.assertFalse((output / "result.json").exists())

    def test_second_reserved_call_can_correct_failed_replay_submission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "output"
            (output / "artifacts").mkdir(parents=True)
            (output / "artifacts" / "check.py").write_text("print('ok')\n")
            task_path = root / "task.json"
            task = {
                "evaluation_id": "opaque",
                "seed": 9,
                "budget": {"max_api_calls": 3},
            }
            task_path.write_text(json.dumps(task))
            calls = []
            responses = iter([
                {"choices": [{"message": {
                    "role": "assistant",
                    "tool_calls": [{
                        "id": "explore",
                        "function": {"name": "list_files", "arguments": "{}"},
                    }],
                }}]},
                {"choices": [{"message": {
                    "role": "assistant",
                    "tool_calls": [{
                        "id": "bad-submit",
                        "function": {
                            "name": "submit_result",
                            "arguments": json.dumps({
                                "classification": "negative_result",
                                "hypothesis": "bounded test",
                                "falsifier": "replay fails",
                                "claim": "no strict improvement established",
                                "evidence": ["bounded exploration ended"],
                                "artifacts": ["check.py"],
                                "replay": [],
                                "theorem_status": "theorem_unchanged",
                            }),
                        },
                    }],
                }}]},
                {"choices": [{"message": {
                    "role": "assistant",
                    "tool_calls": [{
                        "id": "corrected-submit",
                        "function": {
                            "name": "submit_result",
                            "arguments": json.dumps({
                                "classification": "negative_result",
                                "hypothesis": "bounded test",
                                "falsifier": "replay fails",
                                "claim": "no strict improvement established",
                                "evidence": ["bounded exploration ended"],
                                "artifacts": ["check.py"],
                                "replay": [{"argv": ["python3", "check.py"]}],
                                "theorem_status": "theorem_unchanged",
                            }),
                        },
                    }],
                }}]},
            ])

            def fake_chat(payload):
                calls.append(json.loads(json.dumps(payload)))
                return next(responses)

            with mock.patch.object(worker, "OUTPUT", output), mock.patch.object(
                worker, "TASK_PATH", task_path
            ), mock.patch.object(worker, "unix_chat", side_effect=fake_chat):
                self.assertEqual(worker.run_task(task_path), 0)
            self.assertEqual(len(calls), 3)
            self.assertIn(
                "every final Python artifact requires replay",
                calls[2]["messages"][-1]["content"],
            )
            self.assertTrue((output / "result.json").is_file())

    def test_final_calls_are_reserved_for_typed_submission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "output"
            output.mkdir()
            task_path = root / "task.json"
            task = {
                "evaluation_id": "opaque",
                "seed": 9,
                "budget": {"max_api_calls": 3},
            }
            task_path.write_text(json.dumps(task))
            calls = []
            responses = iter([
                {"choices": [{"message": {
                    "role": "assistant",
                    "tool_calls": [{
                        "id": "explore",
                        "function": {"name": "list_files", "arguments": "{}"},
                    }],
                }}]},
                {"choices": [{"message": {
                    "role": "assistant",
                    "tool_calls": [{
                        "id": "submit",
                        "function": {
                            "name": "submit_result",
                            "arguments": json.dumps({
                                "classification": "negative_result",
                                "hypothesis": "bounded test",
                                "falsifier": "replay fails",
                                "claim": "no strict improvement established",
                                "evidence": ["bounded exploration ended"],
                                "artifacts": [],
                                "replay": [],
                                "theorem_status": "theorem_unchanged",
                            }),
                        },
                    }],
                }}]},
            ])

            def fake_chat(payload):
                calls.append(payload)
                return next(responses)

            with mock.patch.object(worker, "OUTPUT", output), mock.patch.object(
                worker, "TASK_PATH", task_path
            ), mock.patch.object(worker, "unix_chat", side_effect=fake_chat):
                self.assertEqual(worker.run_task(task_path), 0)
            self.assertEqual(calls[0]["tool_choice"], "auto")
            self.assertEqual(
                calls[1]["tool_choice"],
                {"type": "function", "function": {"name": "submit_result"}},
            )
            self.assertTrue((output / "result.json").is_file())


if __name__ == "__main__":
    unittest.main()
