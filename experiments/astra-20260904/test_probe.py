"""Independent subset enumeration checks the exact tree DP."""
import importlib.util
import random
import unittest
from pathlib import Path

ROOT = Path(__file__).parent


def load_probe():
    spec = importlib.util.spec_from_file_location('probe', ROOT / 'probe.py')
    if spec is None or spec.loader is None or not (ROOT / 'probe.py').exists():
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def brute(parent):
    counts = [0] * (len(parent) + 1)
    for mask in range(1 << len(parent)):
        if all(not ((mask >> i & 1) and (mask >> p & 1))
               for i, p in enumerate(parent) if p >= 0):
            counts[bin(mask).count('1')] += 1
    while len(counts) > 1 and not counts[-1]:
        counts.pop()
    return counts


class ProbeTests(unittest.TestCase):
    def test_tree_polynomial_matches_actual_independent_sets(self):
        probe = load_probe()
        self.assertIsNotNone(probe, 'exact tree polynomial implementation missing')
        rng = random.Random(993)
        for n in range(1, 13):
            for _ in range(8):
                parent = [-1] + [rng.randrange(i) for i in range(1, n)]
                self.assertEqual(probe.tree_polynomial(parent), brute(parent))

    def test_replayable_search_summary(self):
        probe = load_probe()
        self.assertTrue(hasattr(probe, 'run_search'), 'replayable bounded search missing')
        first = probe.run_search(initial_samples=5, samples_per_hub=5)
        second = probe.run_search(initial_samples=5, samples_per_hub=5)
        self.assertEqual(first, second)
        self.assertEqual(first['samples'], 25)
        self.assertEqual(first['unimodality_failures'], 0)
        self.assertEqual(first['log_concavity_failures'], 0)
        self.assertEqual(sum(r['samples'] for r in first['batches']), 25)

    def test_hub_path_and_real_logconcavity_control(self):
        probe = load_probe()
        self.assertTrue(hasattr(probe, 'hub_path'), 'structural tree constructor missing')
        self.assertTrue(hasattr(probe, 'classify'), 'independent LC/unimodality tests missing')
        # Three hubs joined in a path; all other vertices lie on pendant paths.
        for arms, joins in [(((1, 2), (3,), (1, 1)), (1, 2)),
                            (((2, 2), (2,), (2, 2)), (1, 1))]:
            parent = probe.hub_path(arms, joins)
            deg = [0] * len(parent)
            for i, p in enumerate(parent):
                if p >= 0:
                    deg[i] += 1
                    deg[p] += 1
            self.assertEqual(sum(d >= 3 for d in deg), 3)
            self.assertEqual(len(parent), 1 + sum(joins) + sum(map(sum, arms)))
            self.assertEqual(probe.tree_polynomial(parent), brute(parent))
        # Published T_{3,4,4}: four hubs, each outer hub carries P2 arms.
        parent = [-1]
        for count in (3, 4, 4):
            hub = len(parent)
            parent.append(0)
            for _ in range(count):
                v = len(parent)
                parent.extend([hub, v])
        p = probe.tree_polynomial(parent)
        self.assertEqual(len(parent), 26)
        self.assertFalse(probe.classify(p)['log_concave'])
        self.assertTrue(probe.classify(p)['unimodal'])
        self.assertFalse(probe.classify([1, 3, 2, 4])['unimodal'])
        self.assertTrue(probe.classify([1, 3, 3, 2])['unimodal'])


if __name__ == '__main__':
    unittest.main()
