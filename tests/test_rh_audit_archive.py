"""Preserved audit integrity and scratch replay; never analytic-proof promotion."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "experiments/astra-rh-crt-20260912/audits"


def test_archive_checksum_inventory_covers_all_public_files():
    pins = {}
    for line in (ARCHIVE / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        relative = Path(name)
        assert not relative.is_absolute() and ".." not in relative.parts
        assert name not in pins
        pins[name] = digest
        assert hashlib.sha256((ARCHIVE / name).read_bytes()).hexdigest() == digest
    actual = {p.relative_to(ARCHIVE).as_posix() for p in ARCHIVE.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts and p.name != "SHA256SUMS"}
    assert set(pins) == actual


def test_archive_inventory_and_exclusions_are_explicit():
    manifest = json.loads((ARCHIVE / "MANIFEST.json").read_text())
    inventory = manifest["inventory"]
    assert len(inventory) == len({r["source_locator"] for r in inventory})
    assert len(inventory) == manifest["counts"]["inventory_entries"]
    counts = Counter(row["disposition"] for row in inventory)
    assert counts["preserved"] == manifest["counts"]["preserved_original_entries"]
    assert counts["omitted"] == manifest["counts"]["omitted_original_entries"]
    assert set(counts) == {"preserved", "omitted"}
    workspaces = {row["name"] for row in manifest["workspaces"]}
    assert workspaces == {row["workspace"] for row in inventory}
    assert len(workspaces) == manifest["counts"]["workspaces"]
    for workspace in manifest["workspaces"]:
        assert (ARCHIVE / workspace["main_report"]).is_file()
    for row in inventory:
        if row["disposition"] == "omitted":
            assert row["omission_reason"]
            assert row["public_path"] is None and row["public_sha256"] is None
        else:
            data = (ARCHIVE / row["public_path"]).read_bytes()
            assert hashlib.sha256(data).hexdigest() == row["public_sha256"]
    excluded = [s for s in manifest["checker_specs"] if s["status"] != "standalone-replay"]
    assert len(excluded) == manifest["counts"]["source_dependent_checker_files"]
    assert all(s["missing_dependencies"] and s["reason"] for s in excluded)


def test_archive_harness_optimization_and_path_regressions():
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-m", "unittest", "discover",
         "-s", str(ARCHIVE), "-p", "test_replay.py", "-v"],
        cwd=ROOT, capture_output=True, text=True, timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "skipped" not in result.stderr.lower()
    for name in (
        "test_real_checker_runs_in_fresh_scratch_and_saves_output",
        "test_inherited_optimization_cannot_bypass_historical_assertion",
        "test_json_escaped_roots_are_normalized_in_real_checker_public_outputs",
        "test_path_only_edits_preserve_other_bytes_across_literal_and_json_forms",
    ):
        assert name + " (" in result.stderr


def test_archived_checkers_replay_in_external_scratch(tmp_path):
    before = {p.relative_to(ARCHIVE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in ARCHIVE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    output = tmp_path / "run"
    result = subprocess.run(
        [sys.executable, "-B", str(ARCHIVE / "replay.py"), "--output", str(output)],
        cwd=ROOT, capture_output=True, text=True, timeout=240,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    record = json.loads((output / "REPLAY.json").read_text())
    manifest = json.loads((ARCHIVE / "MANIFEST.json").read_text())
    expected = {s["path"] for s in manifest["checker_specs"] if s["status"] == "standalone-replay"}
    runs = record["runs"]
    assert len(runs) == len(expected)
    assert {r["checker"] for r in runs} == expected
    assert all(r["status"] == "passed" and r["inputs_unchanged"] for r in runs)
    assert record["totals"]["passed"] == len(expected)
    assert record["totals"]["not_replayed_excluded_dependencies"] == len(record["not_replayed"])
    assert record["totals"]["distinct_original_checker_hashes_executed"] == len(
        {r["original_checker_sha256"] for r in runs})
    after = {p.relative_to(ARCHIVE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in ARCHIVE.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert after == before
