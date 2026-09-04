"""Independent subset enumeration tests the compressed tail identity."""
import importlib.util
from pathlib import Path
import random
import unittest

HERE = Path(__file__).parent


def load_tail():
    file = HERE / 'tail.py'
    if not file.exists():
        return None
    spec = importlib.util.spec_from_file_location('tail', file)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decorate(parent, counts):
    result = list(parent)
    for vertex, count in enumerate(counts):
        for _ in range(count):
            middle = len(result)
            result.extend((vertex, middle))
    return result


def brute(parent):
    counts = [0] * (len(parent) + 1)
    for subset in range(1 << len(parent)):
        if all(not ((subset >> v & 1) and (subset >> parent[v] & 1))
               for v in range(1, len(parent))):
            counts[bin(subset).count('1')] += 1
    while counts[-1] == 0:
        counts.pop()
    return counts


class TailTest(unittest.TestCase):
    def test_saved_witnesses_replay_and_poisoned_coefficient_fails(self):
        import shutil
        import tempfile
        import json
        path = HERE / 'verify.py'
        self.assertTrue(path.exists(), 'receipt verifier missing')
        spec = importlib.util.spec_from_file_location('briefcase_verify', path)
        assert spec is not None and spec.loader is not None
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        checked = verifier.verify_all(HERE)
        self.assertEqual(checked['compiled_cores'], 40)
        self.assertEqual(checked['unimodal_witnesses'], 40)
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'data'
            shutil.copytree(HERE, target, ignore=shutil.ignore_patterns('__pycache__'))
            bad_file = target / 'transfer-h4.json'
            records = json.loads(bad_file.read_text())
            records[0]['coefficients'][1] += 1
            bad_file.write_text(json.dumps(records))
            with self.assertRaises(AssertionError):
                verifier.verify_all(target)

    def test_transferred_obstruction_matches_full_tree_dp(self):
        mod = load_tail()
        assert mod is not None
        self.assertTrue(hasattr(mod, 'transfer'), 'obstruction compiler missing')
        old = HERE.parent / 'astra-20260904' / 'probe.py'
        spec = importlib.util.spec_from_file_location('independent_dp', old)
        assert spec is not None and spec.loader is not None
        dp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dp)
        for core in ((-1, 0, 0, 0), (-1, 0, 0, 1, 1, 2, 2)):
            record = mod.transfer(core)
            parent = decorate(core, record['counts'])
            coeff = dp.tree_polynomial(parent)
            k = record['index']
            self.assertEqual(list(coeff[k-1:k+2]), record['coefficients'])
            self.assertLess(coeff[k]**2 - coeff[k-1]*coeff[k+1], 0)
            self.assertEqual(record['defect'], coeff[k]**2 - coeff[k-1]*coeff[k+1])
            self.assertEqual(record['order'], len(parent))

    def test_exact_tail_against_subset_enumeration(self):
        mod = load_tail()
        self.assertIsNotNone(mod, 'compressed-tail implementation missing')
        assert mod is not None
        rng = random.Random(99342)
        for h in range(1, 6):
            for _ in range(10):
                parent = [-1] + [rng.randrange(v) for v in range(1, h)]
                counts = [rng.randrange(2) for _ in range(h)]
                coeff = brute(decorate(parent, counts))
                for depth in (1, 3, len(coeff)):
                    self.assertEqual(mod.tail_coefficients(parent, counts, depth),
                                     tuple(reversed(coeff))[:depth])


if __name__ == '__main__':
    unittest.main()
