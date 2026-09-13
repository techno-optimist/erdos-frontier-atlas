"""Semantic receipt replay, independent of the evidence producer."""
from copy import deepcopy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from test_floor import load

HERE = Path(__file__).resolve().parent


def sample_receipt():
    return {
        "schema": "rh-generic-floor-countermodels-v1",
        "scope": {"generic_coefficients": True, "mobius_coefficients": False,
                  "rh_proved": False, "new_mobius_bound": False},
        "families": [load("floor_transfer").make_family(h)
                     for h in (4, 8, 12, 16, 24, 32)],
    }


def poisoned_receipts():
    """Each altered object is submitted to the same semantic gate."""
    original = sample_receipt()
    cases = {}
    def altered(name):
        case = deepcopy(original)
        cases[name] = case
        return case
    altered("RH promotion")["scope"]["rh_proved"] = True
    altered("Mobius promotion")["scope"]["mobius_coefficients"] = True
    altered("integer scope flag")["scope"]["generic_coefficients"] = 1
    altered("missing scope field")["scope"].pop("new_mobius_bound")
    altered("wrong scale")["families"][0]["x"] += 1
    altered("wrong endpoint")["families"][0]["bins"][0]["right"] -= 1
    altered("wrong sign")["families"][0]["bins"][0]["coefficients"][0][1] = -1
    altered("boolean coefficient")["families"][0]["bins"][0]["coefficients"][0][1] = True
    altered("out of range coefficient")["families"][0]["bins"][0]["coefficients"][0][1] = 2
    altered("float quotient")["families"][0]["bins"][0]["q"] = 1.0
    altered("missing cell")["families"][0]["bins"].pop()
    altered("duplicate family")["families"].append(deepcopy(original["families"][0]))
    altered("empty families")["families"] = []
    altered("oversized allocation")["families"][0]["h"] = 10**100
    altered("boolean h")["families"][0]["h"] = True
    altered("unknown field")["unproved_claim"] = "accepted"
    return cases


class ReceiptTests(unittest.TestCase):
    def test_semantic_gate_replays_and_rejects_false_promotion(self):
        self.assertTrue((HERE / "verify.py").is_file(),
                        "independent receipt checker is not implemented")
        checker = load("verify")
        receipt = sample_receipt()
        result = checker.verify_receipt(receipt)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["families_checked"], len(receipt["families"]))
        self.assertEqual(result["bins_checked"],
                         sum(f["h"] // 4 for f in receipt["families"]))
        self.assertFalse(result["scope"]["rh_proved"])
        poisoned = deepcopy(receipt)
        poisoned["scope"]["rh_proved"] = True
        with self.assertRaises(ValueError):
            checker.verify_receipt(poisoned)


    def test_cli_replay_is_read_only_and_fails_under_optimization(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text(json.dumps(sample_receipt()), encoding="utf-8")
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            command = [sys.executable, "-I", "-B", str(HERE / "verify.py"),
                       "--receipt", str(path)]
            completed = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(completed.stdout.strip().startswith("{"),
                            "checker CLI did not return JSON")
            self.assertTrue(json.loads(completed.stdout)["accepted"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
            bad = sample_receipt()
            bad["scope"]["rh_proved"] = True
            path.write_text(json.dumps(bad), encoding="utf-8")
            poisoned = subprocess.run([sys.executable, "-I", "-O", "-B",
                                      str(HERE / "verify.py"), "--receipt", str(path)],
                                     text=True, capture_output=True)
            self.assertNotEqual(poisoned.returncode, 0)
            self.assertFalse(json.loads(poisoned.stdout)["accepted"])


    def _assert_cli_rejects_json(self, raw, optimized):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            original = raw.encode("utf-8")
            path.write_bytes(original)
            path.chmod(0o444)
            command = [sys.executable, "-I", "-B"]
            if optimized:
                command.append("-O")
            command += [str(HERE / "verify.py"), "--receipt", str(path)]
            completed = subprocess.run(command, text=True, capture_output=True,
                                       timeout=10)
            details = completed.stdout + completed.stderr
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(path.stat().st_mode & 0o777, 0o444)
            self.assertEqual(completed.returncode, 1, details)
            self.assertEqual(completed.stderr, "", details)
            self.assertTrue(completed.stdout.strip().startswith("{"), details)
            verdict = json.loads(completed.stdout)
            self.assertIs(verdict["accepted"], False)
            self.assertIsInstance(verdict["error"], str)
            self.assertTrue(verdict["error"])
            return verdict


    def test_cli_rejects_duplicate_json_keys(self):
        receipt = sample_receipt()
        receipt["families"] = receipt["families"][:1]
        raw = json.dumps(receipt)
        cases = {
            "root schema": raw.replace('"schema": ',
                                       '"schema": null, "schema": ', 1),
            "scope true then false": raw.replace(
                '"rh_proved": false', '"rh_proved": true, "rh_proved": false', 1),
            "scope false then true": raw.replace(
                '"rh_proved": false', '"rh_proved": false, "rh_proved": true', 1),
            "scope equal values": raw.replace(
                '"rh_proved": false', '"rh_proved": false, "rh_proved": false', 1),
            "family h": raw.replace('"h": 4', '"h": 4, "h": 4', 1),
            "bin q": raw.replace('"q": 1', '"q": 1, "q": 1', 1),
            "escaped scope key": raw.replace(
                '"rh_proved": false',
                '"rh_proved": true, "rh_\\u0070roved": false', 1),
            "unknown keys before semantic checks": '{"unknown": 0, "unknown": 1}',
        }
        for label, malformed in cases.items():
            for optimized in (False, True):
                with self.subTest(case=label, optimized=optimized):
                    verdict = self._assert_cli_rejects_json(malformed, optimized)
                    self.assertIn("duplicate", verdict["error"].lower())


    def test_cli_rejects_deep_json(self):
        raw = "[" * 1200 + "]" * 1200
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self._assert_cli_rejects_json(raw, optimized)


    def test_corrupted_receipts_fail_the_real_gate(self):
        checker = load("verify")
        for label, receipt in poisoned_receipts().items():
            with self.subTest(poison=label):
                with self.assertRaises(ValueError):
                    checker.verify_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
