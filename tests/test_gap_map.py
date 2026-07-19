"""Records-lane gap map: contract tests."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "validate_gap_map", ROOT / "tools" / "validate_gap_map.py")
vgm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vgm)


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


# ---------------------------------------------------------------------------
# WS7 epistemic ledger: class computation (charter WS7 — classes are COMPUTED
# from recorded evidence, never asserted).
# ---------------------------------------------------------------------------

def _ev(*pairs):
    return [{"type": t, "artifact": a, "date": "2026-07-18"} for t, a in pairs]


def test_confidence_c0_formal_proof_dominates():
    assert vgm.compute_confidence(_ev(("formal_proof", "proofs/x.lean"))) == "C0"
    # formal_proof wins even alongside anything else
    assert vgm.compute_confidence(
        _ev(("literature", "survey"), ("formal_proof", "proofs/x.lean"),
            ("implementation", "a.py"))) == "C0"


def test_confidence_c1_two_distinct_replications():
    assert vgm.compute_confidence(
        _ev(("implementation", "a.py"), ("implementation", "b.py"))) == "C1"
    # implementation + replay_receipt mix counts, and extra C3-grade items don't demote
    assert vgm.compute_confidence(
        _ev(("implementation", "a.py"), ("replay_receipt", "certificates/x/verify.py"),
            ("numeric_scan", "spot checks"))) == "C1"


def test_confidence_c2_single_verified_implementation():
    assert vgm.compute_confidence(_ev(("implementation", "a.py"))) == "C2"
    assert vgm.compute_confidence(
        _ev(("replay_receipt", "certificates/x/verify.py"), ("literature", "survey"))) == "C2"
    # two items citing the SAME artifact are one replication, not two
    assert vgm.compute_confidence(
        _ev(("implementation", "a.py"), ("replay_receipt", "a.py"))) == "C2"


def test_confidence_c3_conjecture_grade():
    assert vgm.compute_confidence([]) == "C3"
    assert vgm.compute_confidence(_ev(("literature", "as transcribed"))) == "C3"
    assert vgm.compute_confidence(
        _ev(("numeric_scan", "scan to 1e9"), ("literature", "survey"))) == "C3"


def test_ledger_mismatch_fails():
    errors = []
    entry = {"evidence": _ev(("implementation", "a.py")), "confidence": "C1"}
    vgm.check_ledger(errors, "t", entry)
    assert errors and "stored confidence C1 != computed C2" in errors[0]
    # and the honest stamp passes
    errors = []
    entry["confidence"] = "C2"
    vgm.check_ledger(errors, "t", entry)
    assert not errors


def test_ledger_confidence_without_evidence_fails():
    errors = []
    vgm.check_ledger(errors, "t", {"confidence": "C3"})
    assert errors and "confidence present but no evidence" in errors[0]


def test_ledger_evidence_without_confidence_fails():
    errors = []
    vgm.check_ledger(errors, "t", {"evidence": _ev(("literature", "survey"))})
    assert errors and "no stored confidence" in errors[0]


def test_ledger_malformed_evidence_fails():
    errors = []
    vgm.check_ledger(errors, "t", {
        "evidence": [{"type": "vibes", "artifact": "x", "date": "2026-07-18"}],
        "confidence": "C3"})
    assert errors and "bad type" in errors[0]


def test_all_entries_stamped_and_classes_match():
    """Every entry carries evidence[] + confidence, and stored == computed."""
    gm = _load()
    for e in gm["entries"]:
        assert "evidence" in e and "confidence" in e, \
            f"entry {e['problem']} / {e['quantity'][:40]} is unstamped"
        assert e["confidence"] == vgm.compute_confidence(e["evidence"])


def test_ledger_anchor_classes():
    """Charter WS7 exemplars, stated exactly (FRONTIER_CARTOGRAPHY.md)."""
    gm = _load()
    by = {}
    for e in gm["entries"]:
        by.setdefault(e["problem"], []).append(e)
    # A385316 / #979: two independent implementations at the full 1e12 window -> C1
    e979 = [e for e in by[979] if "miner" not in e["provenance"]["added_by"]]
    assert len(e979) == 1 and e979[0]["confidence"] == "C1"
    assert any(it["type"] == "implementation" and "erdos-979" in it["artifact"]
               for it in e979[0]["evidence"])
    # Mollin-Walsh / #1107 lane entry: one scan implementation, receipt fleet-side -> C2
    e1107 = [e for e in by[1107] if "miner" not in e["provenance"]["added_by"]]
    assert len(e1107) == 1 and e1107[0]["confidence"] == "C2"
    # #552: literature bracket + one in-repo lower-bound replay certificate -> C2
    assert all(e["confidence"] == "C2" for e in by[552])
    assert any(it["type"] == "replay_receipt" and "erdos-552-f39" in it["artifact"]
               for e in by[552] for it in e["evidence"])
