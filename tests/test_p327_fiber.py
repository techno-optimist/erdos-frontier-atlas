"""Keep the standalone P327 method bundle in the repository regression gate."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = "experiments/astra-327-fiber-20260912"


def test_p327_fiber_receipt_and_poison_controls():
    result = subprocess.run(
        [sys.executable, "-I", "-B", f"{BUNDLE}/verify.py", "--negative-controls"],
        cwd=ROOT, text=True, capture_output=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data["verdict"] == "PASS"
    assert data["read_only"] is True
    assert data["full_problem_solution"] is False
    assert data["graphs"] == 9
    assert data["prefixes"] == 72
    assert len(data["rejected_controls"]) == 9


def test_p327_fiber_independent_oracles():
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-m", "unittest", "discover",
         "-s", BUNDLE, "-p", "test_*.py", "-q"],
        cwd=ROOT, text=True, capture_output=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
