#!/usr/bin/env python3
"""Replay the general-i P699 search: pin the C engine, run the controls, recheck RESULT.json.

  python3 -I verify.py           # ~3 min: pins, controls, checkpoints and frontier samples
  python3 -I verify.py --full    # also reruns every claim-bearing row of RESULT.json (hours)

Exit status 0 means every check passed. Nothing is written except a temporary executable.
"""
import json
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import general as G  # noqa: E402
import run as R  # noqa: E402

MASK = (1 << 64) - 1


def stats_py(i, X, tmax=None):
    r = G.search(i, X, tmax)
    surv = [[n, j, p or 0] for n, j, p in r["survivors"]]
    return [r["special"], r["checksum"], r["cand12"], r["central"], len(surv)], surv


def pin(exe):
    for X in (10 ** 6, 10 ** 7, 10 ** 8):
        for i in range(3, 11 if X > 10 ** 7 else 14):
            py = stats_py(i, X)
            for mode in ((), ("--plain",)):
                st, surv, _ = R.engine(exe, i, X, *mode)
                assert (st, sorted(surv)) == (py[0], sorted(py[1])), (i, X, mode, st, py)
        print(f"pin: C (sub-progressions and --plain) = Python reference, i = 3..{10 if X > 10 ** 7 else 13}, "
              f"X = {X:.0e}")


def control(exe):
    total = 0
    for i in range(4, 11):
        for tmax in sorted({2, 3} & set(range(2, i))):
            py = stats_py(i, 3000, tmax)
            st, surv, _ = R.engine(exe, i, 3000, "--tmax", tmax)
            brute = []
            for n in range(2 * i + 2, 3001):
                full = G.blocks(n, i)
                low = [b for b in full if b[1] <= tmax]
                brute += [[n, j, G.common_prime(n, j, full) or 0] for j in range(i + 1, n // 2 + 1)
                          if G.passes(n, j, low)]
            assert sorted(surv) == sorted(py[1]) == sorted(brute), (i, tmax)
            assert all(p for _, _, p in brute)
            total += len(brute)
    assert total > 0
    print(f"negative control: requiring only positions t <= 2 or 3, {total} pairs pass for i = 4..10; "
          f"C = Python = brute force, and each pair has a common prime")


def windows(exe):
    for i, lo, X in ((4, 10 ** 6, 10 ** 9), (8, 12345678, 10 ** 10), (6, 10 ** 9 + 7, 3 * 10 ** 9)):
        a, _, _ = R.engine(exe, i, X)
        b, _, _ = R.engine(exe, i, lo)
        c, _, _ = R.engine(exe, i, X, "--from", lo)
        assert c[0] == a[0] - b[0] and c[1] == (a[1] - b[1]) & MASK and c[3] == a[3] - b[3], (i, lo, X)
    one = R.engine(exe, 8, 10 ** 10)[0]
    many = R.run(exe, 8, 10 ** 10, 4)
    assert [many[k] for k in ("special", "checksum", "cand12", "central")] == one[:4]
    print("windows (--from) and shards add up exactly")


def rows(exe, runs, label):
    for want in runs:
        got = R.run(exe, want["i"], want["X"], 4)
        keys = ("special", "checksum", "cand12", "central", "survivors")
        assert all(got[k] == want[k] for k in keys), (want, got)
        assert got["survivors"] == []
        print(f"{label}: i = {want['i']}, X = {want['X']:.0e}: {got['special']} special n, "
              f"{got['cand12']} pairs past t <= 2, {got['central']} central, 0 survivors ({got['seconds']} s)")


def frontier(exe, res, full):
    """The least special n above each bound. i >= 11 only with --full: their pair loops are slow."""
    for f in res["frontier"]:
        if f["i"] > 10 and not full:
            continue
        count, special, surv = R.window(exe, f["i"], f["from"], f["to"], 4)
        assert special[:len(f["least"])] == f["least"] and count == f["special_in_window"] and surv == [], f
    print("frontier samples: the least special n above each searched bound match"
          + ("" if full else " (i <= 10; i = 11..13 with --full)"))


def main():
    full = "--full" in sys.argv[1:]
    res = json.loads((HERE / "RESULT.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        exe = R.build(pathlib.Path(tmp) / "search699")
        pin(exe)
        control(exe)
        windows(exe)
        rows(exe, res["checkpoints"], "checkpoint")
        frontier(exe, res, full)
        if full:
            rows(exe, res["runs"], "run")
    print("all checks passed")
    if full:
        print("receipt-checked: RESULT.json")


if __name__ == "__main__":
    main()
