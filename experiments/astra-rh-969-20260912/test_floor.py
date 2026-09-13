"""Independent small checks; not evidence for RH or an infinite bound."""
import importlib.util
from fractions import Fraction
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    path = HERE / (name + ".py")
    spec = importlib.util.spec_from_file_location("rh_test_" + name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("test module loader unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FloorTransferTests(unittest.TestCase):
    def test_hyperbola_split_matches_direct_definition(self):
        self.assertTrue((HERE / "floor_transfer.py").is_file(),
                        "floor_transfer.py is not implemented")
        transfer = load("floor_transfer")
        coefficients = {1: 1, 2: -1, 3: 0, 4: 1, 7: -1, 11: 1}
        for x in range(61):
            expected = sum(a * (x // (n * n))
                           for n, a in coefficients.items())
            for cutoff in range(1, 10):
                with self.subTest(x=x, cutoff=cutoff):
                    self.assertEqual(transfer.hyperbola_sum(
                        coefficients, x, cutoff), expected)


    def test_hyperbola_rejects_lossy_parameters(self):
        transfer = load("floor_transfer")
        invalid = [
            ({1: 1}, True, 1), ({1: 1}, -1, 1), ({1: 1}, 4.0, 1),
            ({1: 1}, 4, True), ({1: 1}, 4, 0), ({0: 1}, 4, 1),
            ({True: 1}, 4, 1), ({1: True}, 4, 1),
            ({1: 1.0}, 4, 1), ([], 4, 1),
        ]
        for args in invalid:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    transfer.hyperbola_sum(*args)


    def test_balanced_cells_give_exact_countermodels(self):
        transfer = load("floor_transfer")
        self.assertTrue(hasattr(transfer, "make_family"),
                        "countermodel constructor is not implemented")
        for h in (4, 8, 12, 16):
            family = transfer.make_family(h)
            x = h ** 5
            self.assertEqual(family["x"], x)
            self.assertEqual([b["q"] for b in family["bins"]],
                             list(range(h // 4, h // 2)))
            coefficients = {}
            for cell in family["bins"]:
                # Direct floor scan, independent of the constructor's roots.
                members = [n for n in range(h*h, 2*h*h + 1)
                           if x // (n*n) == cell["q"]]
                self.assertEqual((cell["left"], cell["right"]),
                                 (members[0], members[-1]))
                half = len(members) // 2
                expected = [[n, 1] for n in members[:half]]
                expected += [[n, -1] for n in members[-half:]]
                self.assertEqual(cell["coefficients"], expected)
                coefficients.update({n: a for n, a in expected})
            prefix = 0
            for n in range(1, 2*h*h + 1):
                prefix += coefficients.get(n, 0)
                self.assertLessEqual(prefix * prefix, 4*n)
            self.assertEqual(prefix, 0)
            floor_sum = sum(a * (x // (n*n))
                            for n, a in coefficients.items())
            mass = sum((Fraction(a, n*n)
                        for n, a in coefficients.items()), Fraction(0))
            self.assertEqual(floor_sum, 0)
            self.assertGreaterEqual(x * mass, Fraction(h*h, 256))


    def test_family_parameters_are_validated_before_allocation(self):
        transfer = load("floor_transfer")
        for bad in [True, 0, -4, 5, 8.0, "8", 68, 10**100]:
            with self.subTest(h=bad):
                with self.assertRaises(ValueError):
                    transfer.make_family(bad)


    def test_emitter_creates_explicit_receipt_without_overwriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "emitted.json"
            command = [sys.executable, "-I", "-B", str(HERE / "floor_transfer.py"),
                       "--emit", str(path), "--h", "4", "8"]
            completed = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(path.is_file(), "explicit emitter is not implemented")
            original = path.read_bytes()
            receipt = json.loads(original)
            self.assertEqual([f["h"] for f in receipt["families"]], [4, 8])
            self.assertTrue(load("verify").verify_receipt(receipt)["accepted"])
            again = subprocess.run(command, text=True, capture_output=True)
            self.assertNotEqual(again.returncode, 0)
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
