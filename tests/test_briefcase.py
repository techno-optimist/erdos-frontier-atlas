"""The briefcase operators must agree with brute force, and the residual ledger with its evidence."""
import copy
import json
import math
import pathlib
import random
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from briefcaselib import nt, p699, residuals  # noqa: E402

EXPERIMENT = ROOT / "experiments" / "claude-699-general-i-20260928"


def test_primality_and_factoring_are_exact():
    ps = set(nt.primes_upto(50000))
    assert all(nt.is_prime(k) == (k in ps) for k in range(50001))
    for c in (561, 3215031751, 3825123056546413051, 318665857834031151167461,
              3317044064679887385961981, (2 ** 89 - 1) * (2 ** 107 - 1)):
        assert not nt.is_prime(c)
    assert nt.is_prime(2 ** 127 - 1)
    rng = random.Random(7)
    for _ in range(300):
        x = rng.randrange(1, 10 ** 18)
        f = nt.factor(x)
        assert math.prod(p ** e for p, e in f.items()) == x and all(nt.is_prime(p) for p in f)


def test_kummer_carries_are_binomial_valuations():
    for n in range(80):
        for k in range(n + 1):
            c = math.comb(n, k)
            for p in (2, 3, 5, 7):
                assert nt.v_binom(n, k, p) == nt.valuation(c, p)


def test_blocks_are_the_primes_at_least_i_of_the_binomial():
    for i in range(3, 8):
        for n in range(2 * i + 2, 160):
            got = sorted(p for _, _, p in p699.blocks(n, i))
            want = sorted(p for p in nt.factor(math.comb(n, i)) if p >= i)
            assert got == want, (n, i)


def test_row_decision_matches_brute_force():
    for i in range(3, 8):
        for n in range(2 * i + 2, 260):
            rep = p699.row(n, i)
            blk = p699.blocks(n, i)
            passing = [j for j in range(i + 1, n // 2 + 1) if p699.passes(n, j, blk)]
            assert sorted(s["j"] for s in rep["survivors"]) == passing, (n, i)
            truth = all(p699.common_prime(n, j, blk) for j in range(i + 1, n // 2 + 1))
            assert rep["holds"] == truth


def test_special_set_matches_a_direct_scan():
    for i in (3, 4, 5, 8):
        direct = [n for n in range(1, 30001) if p699.special(n, i)]
        assert p699.special_upto(i, 30000) == direct


@pytest.mark.parametrize("n,i", [(162, 4), (2 ** 40, 5), (4376, 8), (10 ** 24 + 2, 7),
                                 (1000000105941565440, 4), (3 ** 40 + 1, 6), (9, 3)])
def test_certificates_round_trip(n, i):
    cert = p699.certify_row(n, i)
    assert p699.verify_row(json.loads(json.dumps(cert)))[0]


def test_tampered_certificates_are_rejected():
    special = p699.certify_row(2 ** 40, 5)
    assert special["kind"] == "special" and special["candidates"]
    bad = copy.deepcopy(special)
    bad["S"][0] = str(int(bad["S"][0]) * 2)
    assert not p699.verify_row(bad)[0]
    bad = copy.deepcopy(special)
    bad["candidates"] = []
    assert not p699.verify_row(bad)[0]
    bad = copy.deepcopy(special)
    fac = bad["factors"]["1"]
    p = next(iter(fac))
    fac[str(int(p) + 2)] = fac.pop(p)
    assert not p699.verify_row(bad)[0]
    relaxed = p699.certify_row(162, 4)          # j = 70 passes positions 1, 2 and fails at 3
    assert any("fails_at" in c for c in relaxed["candidates"])
    bad = copy.deepcopy(relaxed)
    for c in bad["candidates"]:
        if "fails_at" in c:
            c["fails_at"] = 2
    assert not p699.verify_row(bad)[0]
    not_special = p699.certify_row(10 ** 24 + 2, 7)
    bad = copy.deepcopy(not_special)
    bad["kind"] = "special"
    assert not p699.verify_row(bad)[0]
    assert not p699.verify_row({"schema": "nope"})[0]


def test_cli_decides_rows_and_rejects_code():
    run = lambda *a: subprocess.run([sys.executable, "tools/briefcase.py", *a], cwd=ROOT,  # noqa: E731
                                    capture_output=True, text=True)
    p = run("row", "162", "4")
    assert p.returncode == 0 and "holds" in p.stdout
    p = run("row", "10^40+12345", "5")
    assert p.returncode == 0
    p = run("row", "__import__('os')", "4")
    assert p.returncode == 2
    p = run("residuals")
    assert p.returncode == 0 and "p699-i4" in p.stdout


# ------------------------------------------------------------------ the residual ledger

def _result():
    return json.loads((EXPERIMENT / "RESULT.json").read_text())


def test_ledger_records_are_backed_by_replayable_evidence():
    data = residuals.load()
    ids = [r["id"] for r in data["residuals"]]
    assert len(ids) == len(set(ids))
    runs = {(r["i"], r["X"]): r for r in _result()["runs"]}
    for rec in data["residuals"]:
        assert rec["problem"] == 699
        assert (ROOT / rec["reduction"]).is_file() and (ROOT / rec["evidence"]).is_file()
        assert rec["survivors"] == 0
        if rec["operator"]["name"] == "p699.special":
            i = rec["operator"]["args"]["i"]
            assert rec["decide"]["args"]["i"] == i
            run = runs[(i, residuals.bound(rec))]
            assert run["survivors"] == [] and run["special"] == rec["special_at_bound"]
        else:
            assert rec["operator"]["name"] == "p699.special_i3"


def test_ledger_never_carries_a_status():
    text = (ROOT / "atlas" / "residuals.json").read_text()
    assert '"status"' not in text


def test_frontier_members_lie_just_above_the_bound_and_their_rows_hold():
    for rec in residuals.load()["residuals"]:
        members = residuals.frontier(rec, count=2)
        assert members, rec["id"]
        for n in members:
            assert n > residuals.bound(rec) and residuals.member(rec, n)
            assert residuals.decide(rec, n)["holds"]


def test_i3_residual_is_the_i3_note_reduction():
    sys.path.insert(0, str(ROOT / "experiments" / "claude-699-i3-position-20260928"))
    import position  # noqa: E402
    assert all(residuals.special_i3(n) == position.in_reduction(n) for n in range(8, 40000))


def test_calculator_page_ledger_matches_the_evidence():
    page = (ROOT / "tools" / "briefcase.html").read_text()
    assert re.search(r"<title>[^<]{3,40}</title>", page[:8192])
    rows = re.findall(r'\["(\d+)", "10\^(\d+)", (\d+), (\d+), (\d+), (\d+)\]', page)
    assert rows
    runs = {(r["i"], r["X"]): r for r in _result()["runs"]}
    for i, e, special, cand12, central, surv in rows:
        run = runs[(int(i), 10 ** int(e))]
        assert (run["special"], run["cand12"], run["central"], len(run["survivors"])) == (
            int(special), int(cand12), int(central), int(surv))
    assert len(rows) == len(runs)
