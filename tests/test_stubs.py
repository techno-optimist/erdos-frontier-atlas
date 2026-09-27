"""Invariants for the hub stub index (atlas/stubs.json).

The load-bearing guarantee is the LICENSING FIREWALL: no record may carry prose
unless it came from an Apache-2.0 source. These tests fail closed.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "atlas" / "stubs.json"
FORMAL = ROOT.parent / "formal-conjectures" / "FormalConjectures" / "ErdosProblems"


def _load():
    return json.loads(STUBS.read_text())


def test_exists_and_count():
    """Upstream numbers problems 1..N and only ever appends, so the index covers
    exactly 1..N, never fewer than the 1217 of the first pinned snapshot."""
    doc = _load()
    ids = [r["id"] for r in doc["problems"]]
    assert doc["counts"]["total"] == len(ids) >= 1217
    assert ids == list(range(1, len(ids) + 1))


def test_lean_suffix_never_changes_the_informal_state():
    """"(Lean)" marks a formalized solution; upstream keeps an undigested one
    under its informal status, so "open (Lean)" is still open."""
    sys.path.insert(0, str(ROOT / "tools"))
    import build_stubs
    assert build_stubs.map_status("open (Lean)") == ("open", "Open")
    assert build_stubs.map_status("falsifiable") == ("open", "Open")
    assert build_stubs.map_status("proved (Lean)") == ("solved-upstream", "Solved")
    assert build_stubs.map_status("disproved") == ("solved-upstream", "Solved")
    for r in _load()["problems"]:
        if (r["upstream_state_raw"] or "").startswith("open"):
            assert r["upstream_status"] == "Open", r["id"]


def test_ids_unique_and_sorted():
    ids = [r["id"] for r in _load()["problems"]]
    assert ids == sorted(ids)
    assert len(set(ids)) == len(ids)


def test_licensing_firewall_no_link_prose():
    """A link-only record must never carry statement prose — this is the whole
    'complement, never mirror erdosproblems.com' guarantee, enforced as a test."""
    for r in _load()["problems"]:
        if r["statement_source"] == "link":
            assert r["statement"] is None, f"#{r['id']} link-only but carries prose"
        else:
            assert r["statement_source"] == "lean"
            assert r["statement"], f"#{r['id']} lean source but empty statement"


def test_every_stub_links_canonical():
    for r in _load()["problems"]:
        assert r["erdos_url"] == f"https://www.erdosproblems.com/{r['id']}"
        assert "erdosproblems.com" in r["canonical_source"]


def test_lean_join_lossless():
    """Every formalized problem (Lean file) is present as in_lean=True."""
    if not FORMAL.exists():
        pytest.skip("formal-conjectures checkout not present")
    lean_ids = {int(f.stem) for f in FORMAL.glob("*.lean") if f.stem.isdigit()}
    by_id = {r["id"]: r for r in _load()["problems"]}
    missing = [i for i in lean_ids if i not in by_id or not by_id[i]["formalized"]["in_lean"]]
    assert not missing, f"Lean problems not marked in_lean: {missing[:10]}"


def test_deep_refs_resolve():
    problems = json.loads((ROOT / "atlas" / "problems.json").read_text())
    deep_ids = {p["id"] for p in problems.get("problems", problems)}
    for r in _load()["problems"]:
        if r["deep_ref"]:
            assert r["id"] in deep_ids, f"#{r['id']} deep_ref to missing audit record"


def test_schema_valid_sample():
    from jsonschema import Draft202012Validator
    schema = json.loads((ROOT / "atlas" / "stub.schema.json").read_text())
    v = Draft202012Validator(schema)
    problems = _load()["problems"]
    sample = problems[:50] + problems[-50:] + [r for r in problems if r["deep_ref"]]
    for r in sample:
        errs = list(v.iter_errors(r))
        assert not errs, f"#{r['id']}: {errs[0].message}"


def test_compiler_is_deterministic():
    """Re-running the compiler in --check mode reproduces the invariants (the
    rebuild-artifact contract)."""
    if not FORMAL.exists() or not (ROOT.parent / "teorth-erdosproblems").exists():
        pytest.skip("source checkouts not present")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "build_stubs.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
