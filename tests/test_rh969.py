"""Repository gate for the standalone RH/P969 method-obstruction bundle."""
import json
from pathlib import Path
import subprocess
import sys
import shutil

import pytest

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = "experiments/astra-rh-969-20260912"


def test_rh969_semantic_receipt_has_no_rh_or_mobius_promotion():
    result = subprocess.run([sys.executable, "-I", "-B", f"{BUNDLE}/verify.py"],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads(result.stdout)
    assert data["accepted"] is True
    assert data["scope"] == {"generic_coefficients": True, "mobius_coefficients": False,
                             "rh_proved": False, "new_mobius_bound": False}
    assert data["families_checked"] == len(data["families"]) == 6
    assert [row["h"] for row in data["families"]] == [4, 8, 12, 16, 24, 32]
    assert data["bins_checked"] == sum(row["bins_checked"] for row in data["families"]) == 24


def test_rh969_oracles_corruption_and_read_only_controls():
    result = subprocess.run([sys.executable, "-I", "-B", "-m", "unittest", "discover",
                             "-s", BUNDLE, "-p", "test_*.py", "-v"],
                            cwd=ROOT, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


def test_rh969_fixed_cohort_rejects_a_different_valid_family_set(tmp_path, monkeypatch):
    bundle = tmp_path / BUNDLE
    bundle.mkdir(parents=True)
    shutil.copyfile(ROOT / BUNDLE / "verify.py", bundle / "verify.py")
    emitted = subprocess.run(
        [sys.executable, "-I", "-B", str(ROOT / BUNDLE / "floor_transfer.py"),
         "--emit", str(bundle / "receipt.json"),
         "--h", "4", "8", "12", "16", "20", "36"],
        capture_output=True, text=True, timeout=30,
    )
    assert emitted.returncode == 0, emitted.stdout + emitted.stderr
    monkeypatch.setitem(globals(), "ROOT", tmp_path)
    with pytest.raises(AssertionError):
        test_rh969_semantic_receipt_has_no_rh_or_mobius_promotion()
