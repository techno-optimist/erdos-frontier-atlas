import importlib.util
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
