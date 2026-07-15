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


if __name__ == "__main__":
    unittest.main()
