"""The method substrate must not set statuses or impersonate implications."""
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import query_substrate  # noqa: E402


def _run(*args):
    return subprocess.run(
        [sys.executable, "tools/query_substrate.py", *args],
        cwd=ROOT, capture_output=True, text=True)


def test_cli_for_699_names_kernel_methods_and_remaining_gap():
    p = _run("for", "699")
    assert p.returncode == 0, p.stderr
    out = p.stdout
    assert "adjacent-binomial-gcd" in out
    assert "i2-d3-divisor" in out
    assert "i2-complete-gcd" in out
    assert "i3-gcd-of-size" in out
    assert "i3-cancel-coprime-fac" in out
    assert "i3-coprime-six-cancel" in out
    assert "i3-typeA" in out
    assert "i3-typeB1" in out
    assert "i3-typeB2a" in out
    assert "i3-mod4-residual-empty" in out
    assert "i3-p-band" in out
    assert "i3-typeB2b-struct" in out
    assert "kummer-105-digits" in out
    assert "kernel_checked" in out
    assert "not a solution of #699" in out.lower() or "does not close P699" in out
    assert "EEES" in out


def test_cli_for_854_uses_graph_family_and_does_not_claim_spectrum():
    p = _run("for", "854")
    assert p.returncode == 0, p.stderr
    out = p.stdout
    assert "crt-endpoint-safe" in out or "wheel-gap-operator" in out
    assert "A048670" in out
    assert "does not determine" in out.lower() or "not a spectrum" in out.lower()


def test_cli_for_993_does_not_claim_unimodality():
    p = _run("for", "993")
    assert p.returncode == 0, p.stderr
    out = p.stdout
    assert "nonpath-lc-obstruction" in out
    assert "unimodal" in out.lower()
    assert "not" in out.lower()


def test_p327_fiber_method_is_partial_and_302_is_only_a_candidate():
    result = _run("for", "327")
    assert result.returncode == 0, result.stderr
    assert "multiplier-sensitive-fiber-deficit" in result.stdout
    assert "not a solution" in result.stdout.lower()
    hits = query_substrate.applications_for(302)
    ours = [h for h in hits if h["method"] == "multiplier-sensitive-fiber-deficit"]
    assert len(ours) == 1
    assert ours[0]["relation"] == "candidate"


def test_open_board_separates_discharges_from_candidates():
    p = _run("open")
    assert p.returncode == 0, p.stderr
    out = p.stdout
    assert "DISCHARGE" in out
    assert "CANDIDATE" in out
    assert "#699" in out
    # A tag match is not a theorem about that problem.
    assert "not an implication" in out.lower()


def test_candidate_match_is_not_a_discharge():
    hits = query_substrate.applications_for(699)
    kinds = {h["relation"] for h in hits}
    assert "discharges" in kinds
    hits854 = query_substrate.applications_for(854)
    assert any(h["relation"] == "discharges" for h in hits854)
    # Open binomial problems other than 699 may be candidates only.
    hits700 = query_substrate.applications_for(700)
    assert hits700
    assert all(h["relation"] != "discharges" for h in hits700)


def test_substrate_never_writes_stub_status():
    stubs = json.loads((ROOT / "atlas" / "stubs.json").read_text())
    before = json.dumps(stubs, sort_keys=True)
    query_substrate.applications_for(699)
    _run("open")
    after = json.dumps(json.loads((ROOT / "atlas" / "stubs.json").read_text()),
                       sort_keys=True)
    assert before == after


def test_board_is_deterministic():
    a = query_substrate.render_board()
    b = query_substrate.render_board()
    assert a == b
    assert a.startswith("# Method substrate")


def test_committed_board_matches_renderer():
    path = ROOT / "experiments/astra-substrate-20260911/BOARD.md"
    assert path.read_text(encoding="utf-8") == query_substrate.render_board()

def test_rh969_methods_separate_generic_obstruction_from_equivalence():
    hits = query_substrate.applications_for(969)
    ours = {h["method"]: h for h in hits if h["method"] in {
        "reciprocal-square-phase-obstruction", "squarefree-energy-rh-bridge"}}
    assert set(ours) == {"reciprocal-square-phase-obstruction", "squarefree-energy-rh-bridge"}
    assert ours["reciprocal-square-phase-obstruction"]["relation"] == "obstructions"
    bridge = ours["squarefree-energy-rh-bridge"]
    assert bridge["relation"] == "discharges"
    assert "equivalence only" in bridge["note"]
    assert "does not solve P969 or RH" in bridge["note"]
    assert any("unconditional" in s for s in bridge["remaining"])
    # Do not spray this cross-domain bridge onto prime-tag neighbors.
    for pid in (968, 970):
        assert not any(h["method"] in ours for h in query_substrate.applications_for(pid))


def test_rh_scope_guard_rejects_positive_human_and_formal_claims(monkeypatch):
    original = query_substrate.applications_for

    def poisoned(problem):
        hits = original(problem)
        for hit in hits:
            if hit["method"] == "gm-gmrr-variance-transfer":
                hit["note"] = (
                    "Independent model audit; human peer review and formal verification "
                    "have established this transfer; does not solve P969 or RH."
                )
        return hits

    monkeypatch.setattr(query_substrate, "applications_for", poisoned)
    with pytest.raises(AssertionError):
        test_rh_arithmetic_methods_are_discoverable_and_scope_limited()


def test_rh_arithmetic_methods_are_discoverable_and_scope_limited():
    expected = {
        "squarefree-crt-defect-transfer",
        "increment-mellin-continuation",
        "gm-gmrr-variance-transfer",
        "mobius-long-factor-typeI",
        "sparse-square-signed-moment-interface",
    }
    hits = query_substrate.applications_for(969)
    ours = {h["method"]: h for h in hits if h["method"] in expected}
    assert set(ours) == expected
    for hit in ours.values():
        assert hit["relation"] == "discharges"
        assert "does not solve P969 or RH" in hit["note"]
        assert "Independent model audit only" in hit["note"]
        assert "not human peer review or formal verification" in hit["note"]
        assert hit["remaining"]
        assert hit["artifacts"]
        assert all((ROOT / artifact).is_file() for artifact in hit["artifacts"])
    assert "actual centered-defect energy" in " ".join(ours["squarefree-crt-defect-transfer"]["remaining"])
    assert "not original integral convergence" in ours["increment-mellin-continuation"]["statement"]
    assert "4/7-epsilon" in ours["gm-gmrr-variance-transfer"]["statement"]
    assert "k=2" in ours["mobius-long-factor-typeI"]["statement"]
    assert "not a lower bound for the full moment" in ours["sparse-square-signed-moment-interface"]["statement"]
    for pid in (121, 968, 970):
        assert not any(h["method"] in expected for h in query_substrate.applications_for(pid))
