import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SPEC = importlib.util.spec_from_file_location(
    "foundry_canonical_verify",
    Path(__file__).parents[1] / "tools" / "foundry_canonical_verify.py",
)
canonical = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(canonical)
ROOT = Path(__file__).parents[1]


def projective_plane_order_five():
    q = 5
    affine = {(x, y): x * q + y for x in range(q) for y in range(q)}
    infinity = {slope: q * q + slope for slope in range(q + 1)}
    lines = []
    for slope in range(q):
        for intercept in range(q):
            lines.append([
                *(affine[(x, (slope * x + intercept) % q)] for x in range(q)),
                infinity[slope],
            ])
    for x in range(q):
        lines.append([*(affine[(x, y)] for y in range(q)), infinity[q]])
    lines.append([infinity[slope] for slope in range(q + 1)])
    return {"edges": lines}


class CanonicalVerifierTests(unittest.TestCase):
    def test_distinct_subset_sum_checker_is_exact(self):
        witness = {"set": [1 << index for index in range(11)]}
        with self.assertRaisesRegex(canonical.CanonicalVerificationError, "does not improve"):
            canonical.verify_distinct_subset_sums(witness)
        with mock.patch.object(canonical, "DISTINCT_SUBSET_SUMS_FROZEN_UPPER", 2000):
            report = canonical.verify_distinct_subset_sums(witness)
        self.assertEqual(report["subset_sums"], 2048)
        broken = {"set": [1, 2, 3, 8, 16, 32, 64, 128, 256, 512, 1024]}
        with self.assertRaisesRegex(canonical.CanonicalVerificationError, "same sum"):
            canonical.verify_distinct_subset_sums(broken)

    def test_q6_checker_validates_projective_plane_and_rejects_five_cover(self):
        witness = projective_plane_order_five()
        with self.assertRaisesRegex(canonical.CanonicalVerificationError, "does not improve"):
            canonical.verify_q6(witness)
        with mock.patch.object(canonical, "Q6_FROZEN_UPPER", 32):
            report = canonical.verify_q6(witness)
        self.assertEqual(report["cover_number"], 6)
        self.assertEqual(report["edges"], 31)
        star = {"edges": [[0, *range(1 + 5 * i, 6 + 5 * i)] for i in range(6)]}
        with self.assertRaisesRegex(canonical.CanonicalVerificationError, "hitting set"):
            canonical.verify_q6(star)

    def test_van_der_waerden_checker_uses_exact_bitset_scan(self):
        witness = None
        with mock.patch.dict(
            canonical.VAN_DER_WAERDEN_FROZEN_WITNESS_LENGTH, {3: 7}, clear=True
        ):
            for mask in range(1 << 8):
                candidate = {"k": 3, "coloring": [(mask >> i) & 1 for i in range(8)]}
                try:
                    report = canonical.verify_van_der_waerden(candidate)
                except canonical.CanonicalVerificationError:
                    continue
                witness = report
                break
        self.assertIsNotNone(witness)
        self.assertEqual(witness["certified_lower_bound"], 9)

    def test_c4_star_checker_does_not_upgrade_known_21_vertex_duplicate(self):
        document = json.loads(
            (ROOT / "certificates" / "erdos-552" / "witnesses.json").read_text()
        )
        known = document["lower_bound_witnesses"][0]
        with self.assertRaisesRegex(canonical.CanonicalVerificationError, "22 vertices"):
            canonical.verify_c4_star(known)

    def test_candidate_verdict_is_task_result_and_source_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "candidate"
            artifacts = output / "artifacts"
            artifacts.mkdir(parents=True)
            contract = json.loads(canonical.CONTRACTS.read_text())["contracts"]["1"]
            packet = {
                "schema": "p42-foundry-eval-task-v1",
                "evaluation_id": "eval_erdos_1",
                "seed": 17,
                "target": {"id": 1},
                "canonical_artifact_contract": contract,
            }
            task_path = root / "task.json"
            task_path.write_text(json.dumps(packet))
            witness_path = artifacts / contract["artifact_path"]
            witness_path.write_text(json.dumps({"set": [1 << i for i in range(11)]}))
            result = {
                "schema": "p42-foundry-candidate-result-v2",
                "evaluation_id": packet["evaluation_id"],
                "seed": packet["seed"],
                "task_packet_sha256": canonical.sha256_bytes(canonical.canonical_bytes(packet)),
                "artifacts": [{
                    "path": contract["artifact_path"],
                    "sha256": canonical.sha256_file(witness_path),
                    "bytes": witness_path.stat().st_size,
                }],
            }
            (output / "result.json").write_text(json.dumps(result))
            with mock.patch.object(canonical, "DISTINCT_SUBSET_SUMS_FROZEN_UPPER", 2000):
                verified = canonical.verify_candidate(output, task_path)
            verdict = canonical.build_verdict(verified, "trusted-revision")
            self.assertEqual(verdict["verdict"], "accepted")
            self.assertEqual(verdict["utility_units"], 8)
            self.assertEqual(verdict["verifier_id"], contract["verifier_id"])
            self.assertEqual(
                verdict["task_packet_sha256"], result["task_packet_sha256"]
            )


if __name__ == "__main__":
    unittest.main()
