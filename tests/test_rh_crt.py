"""CI replay of the published bounded CRT package, not analytic proof checking."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
BUNDLE = ROOT / "experiments/astra-rh-crt-20260912"


def test_crt_committed_cohort_is_complete_and_semantically_replays():
    before = hashlib.sha256((BUNDLE / "receipt.json").read_bytes()).hexdigest()
    result = subprocess.run(
        [sys.executable, "-I", "-B", "verify.py", "receipt.json"],
        cwd=BUNDLE, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = json.loads(result.stdout)
    assert verdict["passed"] is True
    assert verdict["rh_proved"] is False
    assert verdict["scope"] == "uniform-residue-phase-only"
    receipt = json.loads((BUNDLE / "receipt.json").read_text())
    prime_sets = ((), (2,), (3,), (2, 3), (2, 5), (3, 5), (2, 3, 5))
    lengths = (0, 1, 2, 3, 4, 9, 16, 36, 900, 10**30 + 2)
    expected = {(primes, h) for primes in prime_sets for h in lengths}
    actual = [(tuple(case["primes"]), case["H"]) for case in receipt["cases"]]
    assert len(actual) == len(set(actual)) == len(expected) == 70
    assert set(actual) == expected
    assert verdict["case_count"] == receipt["case_count"] == len(expected)
    assert verdict["distinct_prime_sets"] == len(prime_sets)
    assert hashlib.sha256((BUNDLE / "receipt.json").read_bytes()).hexdigest() == before


def test_crt_independent_oracles_and_poison_controls():
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-m", "unittest", "discover",
         "-s", ".", "-p", "test_*.py", "-v"],
        cwd=BUNDLE, capture_output=True, text=True, timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_crt_historical_software_snapshot_and_public_review_hashes():
    status = json.loads((BUNDLE / "REVIEW_STATUS.json").read_text())
    expected_sources = {"kernel.py", "verify.py", "test_kernel.py", "test_receipt.py"}
    review = status["code_review"]
    assert set(review["source_sha256"]) == expected_sources
    assert type(review["fully_reviewed_file_count"]) is int
    assert review["fully_reviewed_file_count"] == len(expected_sources)
    for name, digest in review["source_sha256"].items():
        assert hashlib.sha256((BUNDLE / name).read_bytes()).hexdigest() == digest
    portability = json.loads((BUNDLE / "portability.json").read_text())
    expected = {
        "code_review.json": status["code_review"]["report_sha256"],
        "typeI_review.json": status["Arithmetic_followup"]["adversarial_reviews"]["typeI"]["verdict_sha256"],
        "diagonal_review.json": status["Arithmetic_followup"]["adversarial_reviews"]["diagonal"]["verdict_sha256"],
    }
    records = portability["files"]
    assert len(records) == len(expected)
    assert {row["file"] for row in records} == set(expected)
    for row in records:
        assert row["original_sha256"] == expected[row["file"]]
        assert row["semantic_changes"] is False
        assert row["replacement_count"] > 0
        data = (BUNDLE / row["file"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == row["public_sha256"]
        assert json.loads(data)["passed"] is True


@pytest.mark.parametrize("poison", ["empty", "missing", "wrong_count", "bool_count"])
def test_crt_historical_source_coverage_rejects_incomplete_metadata(tmp_path, monkeypatch, poison):
    clone = tmp_path / "bundle"
    shutil.copytree(BUNDLE, clone, ignore=shutil.ignore_patterns("audits", "__pycache__"))
    path = clone / "REVIEW_STATUS.json"
    status = json.loads(path.read_text())
    review = status["code_review"]
    if poison == "empty":
        review["source_sha256"] = {}
    elif poison == "missing":
        review["source_sha256"].pop("kernel.py")
    elif poison == "wrong_count":
        review["fully_reviewed_file_count"] = 3
    else:
        review["fully_reviewed_file_count"] = True
    path.write_text(json.dumps(status))
    monkeypatch.setitem(globals(), "BUNDLE", clone)
    with pytest.raises(AssertionError):
        test_crt_historical_software_snapshot_and_public_review_hashes()


def test_crt_verifier_is_standalone_read_only_and_rejects_scope_promotion(tmp_path):
    for name in ("verify.py", "receipt.json"):
        shutil.copyfile(BUNDLE / name, tmp_path / name)
        (tmp_path / name).chmod(0o444)
    assert not (tmp_path / "kernel.py").exists()
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in tmp_path.iterdir()}
    command = [sys.executable, "-I", "-B", "verify.py", "receipt.json"]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True,
                            text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["passed"] is True
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in tmp_path.iterdir()} == before

    poisoned = json.loads((tmp_path / "receipt.json").read_text())
    poisoned["rh_proved"] = True
    (tmp_path / "poison.json").write_text(json.dumps(poisoned))
    for optimization in ([], ["-O"]):
        rejected = subprocess.run(
            [sys.executable, *optimization, "-I", "-B", "verify.py", "poison.json"],
            cwd=tmp_path, capture_output=True, text=True, timeout=30,
        )
        assert rejected.returncode == 1, rejected.stdout + rejected.stderr
        assert json.loads(rejected.stdout)["passed"] is False
    assert all(hashlib.sha256((tmp_path / name).read_bytes()).hexdigest() == digest
               for name, digest in before.items())
