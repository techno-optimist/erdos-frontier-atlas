"""Exact lemma checks against the existing producer, not a new RH verifier."""
from fractions import Fraction
import unittest

from test_floor import load


class PersistenceTests(unittest.TestCase):
    def test_interval_jump_bound_with_rational_offsets(self):
        producer = load("floor_transfer")
        for h in (4, 8, 12, 16, 24, 32, 36, 64):
            family = producer.make_family(h)
            x = h**5
            coefficients = {n: a for cell in family["bins"]
                            for n, a in cell["coefficients"]}
            upper = Fraction(h**4, 256)
            for offset in sorted({Fraction(0), Fraction(1, 2), upper/2, upper}):
                with self.subTest(h=h, offset=offset):
                    jumps = {n: (Fraction(x) + offset) // (n*n) - x // (n*n)
                             for n in coefficients}
                    self.assertTrue(all(j in (0, 1) for j in jumps.values()))
                    bound = offset/(4*h*h) + Fraction(h, 4)
                    self.assertLessEqual(sum(jumps.values()), bound)
                    self.assertLessEqual(sum(coefficients[n]*j for n, j in jumps.items()), bound)

    def test_energy_and_persistence_constant_algebra(self):
        # Coefficient identities, not a finite substitute for the all-H proof.
        self.assertEqual(Fraction(1, 256)*Fraction(1, 512)**2, Fraction(1, 2**26))
        self.assertEqual(Fraction(8, 5)-Fraction(3, 2), Fraction(1, 10))
        margin = Fraction(1, 256)-Fraction(1, 1024)-Fraction(1, 512)
        self.assertEqual(margin, Fraction(1, 1024))
        self.assertGreaterEqual(4096*margin, Fraction(9, 4))
        self.assertLess(2**8, 4**5)


if __name__ == "__main__":
    unittest.main()
