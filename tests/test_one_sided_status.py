"""Regression: one-sided / independence upstream labels are NOT solved.

tools/build_stubs.py once mapped every non-open teorth state to solved-upstream,
so 'not provable' / 'not disprovable' (one direction settled) and 'independent'
showed as Solved. #736 #739 #1154 #1169 #1171 #1174 #1176 were the reported cases.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_stubs import map_status  # noqa: E402

REPORTED = {736, 739, 1154, 1169, 1171, 1174, 1176}


def _stubs():
    return {r["id"]: r for r in json.loads((ROOT / "atlas" / "stubs.json").read_text())["problems"]}


def test_map_status_one_sided_labels():
    for lab in ("not provable", "not disprovable", "not provable (Lean)", "not disprovable (Lean)"):
        assert map_status(lab) == ("one-sided-upstream", "One-sided")
    assert map_status("independent") == ("independent-upstream", "Independent")
    assert map_status("proved")[0] == "solved-upstream"
    assert map_status("disproved (Lean)")[0] == "solved-upstream"
    assert map_status("decidable")[0] == "open"


def test_reported_seven_not_solved():
    s = _stubs()
    for n in REPORTED:
        r = s[n]
        assert r["status"] == "one-sided-upstream", (n, r["status"])
        assert r["upstream_status"] == "One-sided"
        assert r["upstream_state_raw"].replace(" (Lean)", "") in ("not provable", "not disprovable")


def test_no_one_sided_or_independent_label_is_solved():
    for n, r in _stubs().items():
        b = (r["upstream_state_raw"] or "").replace(" (Lean)", "")
        if b in ("not provable", "not disprovable", "independent"):
            assert "solved" not in r["status"], (n, b, r["status"])
