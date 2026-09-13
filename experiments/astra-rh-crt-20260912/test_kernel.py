"""Direct residue-phase enumeration: independent of the divisor formula."""
from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def load_kernel(test):
    path = HERE / "kernel.py"
    test.assertTrue(path.is_file(), "Missing CRT variance implementation")
    spec = importlib.util.spec_from_file_location("crt_kernel", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load local test subject")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def phase_oracle(primes, h):
    period = 1
    for p in primes:
        period *= p * p
    pattern = [int(all(n % (p * p) for p in primes)) for n in range(period)]
    allowed = sum(pattern)
    density = Fraction(allowed, period)
    cycles, rem = divmod(h, period)
    prefix = [0]
    for value in pattern + pattern:
        prefix.append(prefix[-1] + value)
    counts = [cycles * allowed + prefix[n + rem + 1] - prefix[n + 1]
              for n in range(period)]
    assert sum(counts) == h * allowed
    return density, sum(((Fraction(c) - h * density) ** 2 for c in counts), Fraction()) / period


class KernelTests(unittest.TestCase):
    def test_variance_matches_direct_residue_averaging(self):
        kernel = load_kernel(self)
        for primes in ([], [2], [3], [2, 3], [2, 5], [3, 5], [2, 3, 5]):
            for h in (0, 1, 2, 3, 4, 9, 16, 36, 900, 10**30 + 2):
                with self.subTest(primes=primes, h=h):
                    self.assertEqual(kernel.variance(primes, h), phase_oracle(primes, h)[1])


    def test_variance_rejects_invalid_or_lossy_parameters(self):
        kernel = load_kernel(self)
        invalid = [([2], True), ([2], 1.5), ([2], Fraction(1, 2)),
                   ([2], -1), ([2], 1 << 513), ([2, 2], 1),
                   ([3, 2], 1), ([4], 1), ([True], 1), ([2.0], 1),
                   ([101], 1), ("2", 1), (None, 1),
                   ([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41], 1)]
        for primes, h in invalid:
            with self.assertRaises(ValueError, msg=repr((primes, h))):
                kernel.variance(primes, h)


    def test_real_kernel_obeys_prime_addition(self):
        kernel = load_kernel(self)
        self.assertTrue(hasattr(kernel, "phase_kernel"), "Missing real kernel extension")
        for primes in ([], [2], [3], [2, 3]):
            for p in (2, 3, 5):
                if p in primes:
                    continue
                for t in (Fraction(0), Fraction(1, 3), Fraction(17, 5), Fraction(48)):
                    enlarged = sorted(primes + [p])
                    expected = (1 - Fraction(2, p*p)) * kernel.phase_kernel(primes, t)
                    expected += kernel.phase_kernel(primes, t / (p*p))
                    self.assertEqual(kernel.phase_kernel(enlarged, t), expected)
        for bad in (True, 0.5, -1, Fraction(1, 1 << 513)):
            with self.assertRaises(ValueError):
                kernel.phase_kernel([2], bad)


    def test_normalized_refinement_is_an_orthogonal_increment(self):
        kernel = load_kernel(self)
        self.assertTrue(hasattr(kernel, "refinement_energy"), "Missing normalized refinement operator")
        for small, large in (([], [2]), ([2], [2, 3]), ([3], [2, 3]), ([2, 3], [2, 3, 5])):
            period = 1
            for p in large:
                period *= p*p
            for h in (0, 1, 2, 3, 9):
                densities = [phase_oracle(ps, 0)[0] for ps in (small, large)]
                expected = Fraction()
                for n in range(period):
                    values = []
                    for ps, rho in zip((small, large), densities):
                        count = sum(all((n+j) % (p*p) for p in ps) for j in range(1, h+1))
                        values.append(Fraction(count, 1) / rho - h)
                    expected += (values[1] - values[0]) ** 2
                expected /= period
                self.assertEqual(kernel.refinement_energy(small, large, h), expected)
                self.assertGreaterEqual(expected, 0)
        with self.assertRaises(ValueError):
            kernel.refinement_energy([2, 5], [2, 3], 1)


if __name__ == "__main__":
    unittest.main()
