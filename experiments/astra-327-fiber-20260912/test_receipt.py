"""Receipt acceptance is a semantic gate, not a digest-only check."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def verifier():
    path = HERE / 'verify.py'
    if not path.exists():
        raise AssertionError('verify.py implementation is missing')
    spec = importlib.util.spec_from_file_location('p327_verify', path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ReceiptTest(unittest.TestCase):
    def test_compiler_receipt_passes_independent_gate(self):
        v = verifier()
        data = v.build_receipt()
        summary = v.check_receipt(data)
        self.assertEqual(summary['verdict'], 'PASS')
        self.assertEqual(len(data['cases']), 6)
        self.assertEqual(summary['graphs'], 9)
        self.assertEqual(summary['prefixes'], 72)
        self.assertEqual(data['node'], 'P327')
        self.assertFalse(data['full_problem_solution'])

    def test_poisoned_evidence_uses_same_acceptance_gate(self):
        v = verifier()
        self.assertTrue(hasattr(v,'negative_controls'), 'negative_controls is missing')
        rejected = v.negative_controls(v.build_receipt())
        self.assertEqual(set(rejected), {'wrong_alpha','invented_edge','wrong_weight',
                                        'missing_state','wrong_bound','wrong_witness',
                                        'wrong_delta','bool_for_integer','missing_case'})

    def test_cli_emit_readonly_replay_and_corruption_rejection(self):
        import hashlib
        import json
        import subprocess
        import sys
        import tempfile
        v = verifier()
        self.assertTrue(hasattr(v,'main'), 'CLI main is missing')
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'receipt.json'
            command = [sys.executable,'-I','-B',str(HERE/'verify.py')]
            emitted = subprocess.run(command+['--emit',str(path)],capture_output=True,text=True)
            self.assertEqual(emitted.returncode,0,emitted.stdout+emitted.stderr)
            original = path.read_bytes()
            replay = subprocess.run(command+['--receipt',str(path),'--negative-controls'],
                                    capture_output=True,text=True)
            self.assertEqual(replay.returncode,0,replay.stdout+replay.stderr)
            self.assertEqual(json.loads(replay.stdout)['verdict'],'PASS')
            self.assertEqual(hashlib.sha256(original).digest(),hashlib.sha256(path.read_bytes()).digest())
            duplicate = subprocess.run(command+['--emit',str(path)],capture_output=True,text=True)
            self.assertNotEqual(duplicate.returncode,0)
            bad = json.loads(original)
            bad['cases'][1]['coefficient'] = '1/100'
            path.write_text(json.dumps(bad))
            before = path.read_bytes()
            failed = subprocess.run(command+['--receipt',str(path)],capture_output=True,text=True)
            self.assertNotEqual(failed.returncode,0)
            self.assertEqual(json.loads(failed.stdout)['verdict'],'FAIL')
            self.assertEqual(path.read_bytes(),before)
            path.write_text('{bad json')
            malformed = subprocess.run(command+['--receipt',str(path)],capture_output=True,text=True)
            self.assertNotEqual(malformed.returncode,0)


if __name__ == '__main__':
    unittest.main()
