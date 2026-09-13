"""Semantic replay tests; fixtures come from direct enumeration."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest
from test_kernel import phase_oracle

HERE = Path(__file__).resolve().parent


def load_verifier(test):
    path = HERE / "verify.py"
    test.assertTrue(path.is_file(), "Missing independent semantic verifier")
    spec = importlib.util.spec_from_file_location("crt_verify", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load local verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture():
    cases = []
    for primes, h in (([2], 1), ([2, 3, 5], 3)):
        rho, value = phase_oracle(primes, h)
        cases.append(dict(primes=primes, H=h, density=str(rho), variance=str(value)))
    return dict(schema="squarefree-crt-phase-v1", problem="P969",
                scope="uniform-residue-phase-only", rh_proved=False,
                case_count=len(cases), cases=cases,
                adverse_phase=dict(primes=[2,3,5], H=3, start=547,
                                   count=0, squared_error="2304/625"))


class ReceiptTests(unittest.TestCase):
    def test_accepts_exact_independently_enumerated_fixture(self):
        verifier = load_verifier(self)
        verdict = verifier.verify_receipt(fixture())
        self.assertTrue(verdict["passed"])
        self.assertEqual(verdict["case_count"], 2)


    def test_rejects_false_values_domains_counts_and_promotion(self):
        verifier = load_verifier(self)
        bad = []
        for key, value in (("rh_proved", True), ("rh_proved", 0),
                           ("scope", "actual-finite-interval-bound"),
                           ("case_count", 3), ("problem", "P20"),
                           ("schema", "squarefree-crt-phase-v0")):
            doc = fixture(); doc[key] = value; bad.append(doc)
        for key, value in (("variance", "0"), ("density", "6/8"),
                           ("density", 0.75), ("H", True),
                           ("H", -1), ("H", 1 << 513),
                           ("primes", [2,2])):
            doc = fixture(); doc["cases"][0][key] = value; bad.append(doc)
        doc=fixture(); doc["cases"][1]["primes"]=[5,3,2]; bad.append(doc)
        doc=fixture(); rho,v=phase_oracle([4],1)
        doc["cases"][0]=dict(primes=[4],H=1,density=str(rho),variance=str(v)); bad.append(doc)
        doc=fixture(); doc["cases"].append(copy.deepcopy(doc["cases"][0])); doc["case_count"]+=1; bad.append(doc)
        doc=fixture(); doc["cases"]=[]; doc["case_count"]=0; bad.append(doc)
        doc=fixture(); doc["extra"]=True; bad.append(doc)
        doc=fixture(); doc["adverse_phase"]["count"]=1; bad.append(doc)
        doc=fixture(); doc["adverse_phase"]["start"]=0
        doc["adverse_phase"]["count"]=3
        doc["adverse_phase"]["squared_error"]=str((3-3*Fraction(16,25))**2); bad.append(doc)
        for primes in ([101], [2,3,5,7,11], None):
            doc=fixture(); doc["cases"][0]["primes"]=primes; bad.append(doc)
        doc=fixture(); doc["cases"]*=65; doc["case_count"]=len(doc["cases"]); bad.append(doc)
        doc=fixture(); doc["adverse_phase"]["H"]=1 << 512; bad.append(doc)
        bad.extend((None, [], {"schema":"squarefree-crt-phase-v1"}))
        for index, doc in enumerate(bad):
            with self.assertRaises(ValueError, msg="poison %d" % index):
                verifier.verify_receipt(doc)


    def test_cli_is_read_only_and_rejects_ambiguous_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.json"
            raw = json.dumps(fixture())
            path.write_text(raw)
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            command = [sys.executable, "-I", "-B", str(HERE / "verify.py"), str(path)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('"passed"', result.stdout, "Missing machine verdict")
            self.assertTrue(json.loads(result.stdout)["passed"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)
            duplicate = raw.replace('"rh_proved": false', '"rh_proved": true, "rh_proved": false')
            float_doc = fixture(); float_doc["cases"][0]["H"] = 1.0
            nan_doc = fixture(); nan_doc["cases"][0]["variance"] = float("nan")
            integer_doc = fixture(); integer_doc["cases"][0]["H"] = 10**180
            for text in (duplicate, json.dumps(float_doc), json.dumps(nan_doc),
                         json.dumps(integer_doc), " "*262145):
                path.write_text(text)
                before = hashlib.sha256(path.read_bytes()).hexdigest()
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(json.loads(result.stdout)["passed"])
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)


    def test_explicit_producer_replays_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            command = [sys.executable, "-I", "-B", str(HERE / "kernel.py"), "--emit", str(path)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(path.is_file(), "Explicit producer did not emit a receipt")
            doc = json.loads(path.read_text())
            sets = ([], [2], [3], [2,3], [2,5], [3,5], [2,3,5])
            lengths = (0,1,2,3,4,9,16,36,900,10**30+2)
            expected = {(tuple(ps), h) for ps in sets for h in lengths}
            self.assertEqual({(tuple(c["primes"]), c["H"]) for c in doc["cases"]}, expected)
            self.assertEqual(doc["case_count"], len(expected))
            replay = subprocess.run([sys.executable,"-I","-B",str(HERE/"verify.py"),str(path)],
                                    capture_output=True,text=True)
            self.assertEqual(replay.returncode, 0, replay.stdout)
            self.assertEqual(json.loads(replay.stdout)["case_count"], len(expected))
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            again = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(again.returncode, 2)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)


    def test_deep_json_rejection_still_returns_a_machine_verdict(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"deep.json"
            path.write_text("["*1200+"]"*1200)
            result=subprocess.run([sys.executable,"-I","-B",str(HERE/"verify.py"),str(path)],
                                  capture_output=True,text=True)
            self.assertEqual(result.returncode,1)
            self.assertIn('"passed"',result.stdout,"Deep JSON escaped the machine-verdict contract")
            self.assertFalse(json.loads(result.stdout)["passed"])


if __name__ == "__main__":
    unittest.main()
