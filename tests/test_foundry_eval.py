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


if __name__ == "__main__":
    unittest.main()
