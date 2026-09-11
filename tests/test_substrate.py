"""The method substrate must not set statuses or impersonate implications."""
import json
import pathlib
import subprocess
import sys

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
