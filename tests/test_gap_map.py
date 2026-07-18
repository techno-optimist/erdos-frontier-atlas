"""Records-lane gap map: contract tests."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load():
    return json.loads((ROOT / "atlas" / "gap_map.json").read_text())


def test_validator_passes():
    p = subprocess.run([sys.executable, str(ROOT / "tools" / "validate_gap_map.py")],
                       capture_output=True, text=True)
    assert p.returncode == 0, f"validator failed:\n{p.stdout}\n{p.stderr}"


def test_seed_coverage():
    gm = _load()
    assert gm["schema"] == "erdos-gap-map-v1"
    assert len(gm["entries"]) >= 12
    # every seed kind is represented, so downstream lanes see all shapes
    kinds = {e["kind"] for e in gm["entries"]}
    assert {"value_gap", "next_cell", "bounded_below_only",
            "bounded_above_only", "not_gap_shaped"} <= kinds


def test_unique_and_sourced():
    gm = _load()
    keys = [(e["problem"], e["quantity"]) for e in gm["entries"]]
    assert len(keys) == len(set(keys))
    for e in gm["entries"]:
        for b in (e["lower"], e["upper"]):
            if b is not None:
                assert b["value"].strip() and b["source"].strip()
        assert e["provenance"]["checked"], f"entry {e['problem']} lacks checked sources"


def test_problems_exist_in_hub():
    gm = _load()
    stubs = json.loads((ROOT / "atlas" / "stubs.json").read_text())
    ids = {r["id"] for r in stubs["problems"]}
    for e in gm["entries"]:
        assert e["problem"] in ids
