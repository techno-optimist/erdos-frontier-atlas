"""The residual ledger: what a proved reduction leaves open, as executable predicates.

atlas/residuals.json records, for each open slice that a proved reduction has cut down, the
residual set (the only places a counterexample can still live), the operator that decides
membership, how far the residual has been searched, and the command that replays the search.

The ledger never sets a status. "Searched through X with no survivor" is replayable evidence
recorded in the linked note, not a proof of the slice.
"""
import heapq
import json
import pathlib

from . import p699

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = ROOT / "atlas" / "residuals.json"
SCHEMA = "erdos-frontier-atlas-residuals-v1"


def load(path=LEDGER):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError(f"{path}: schema is not {SCHEMA}")
    return data


def get(rid, path=LEDGER):
    for rec in load(path)["residuals"]:
        if rec["id"] == rid:
            return rec
    raise KeyError(rid)


def bound(rec):
    """searched_through as an int ("1e18" and "10^18" style strings allowed)."""
    s = str(rec["searched_through"]).replace("10^", "1e")
    return int(float(s)) if "e" in s else int(s)


# ------------------------------------------------------------------ operators

def special_i3(n):
    """The i = 3 note's residual: 4 | n and (2KA-1)(2KA-2) <= (4/sqrt 3) K^3."""
    if n < 8 or n % 4:
        return False
    a = (n & -n).bit_length() - 1
    odd = n >> a
    eps = 1 if odd % 3 == 0 and odd % 9 != 0 else 0
    A = odd // 3 ** eps
    K = 2 ** (a - 1) * 3 ** eps
    L = (2 * K * A - 1) * (2 * K * A - 2)
    return 3 * L * L <= 16 * K ** 6


def member(rec, n):
    """True when n lies in the residual of `rec`."""
    op = rec["operator"]
    if op["name"] == "p699.special_i3":
        return special_i3(n)
    if op["name"] == "p699.special":
        i = op["args"]["i"]
        central = n % 2 == 0 and n >= 2 * i + 2 and p699.split(n - 1, i)[1] == 1
        return p699.special(n, i) or central
    raise KeyError(f"unknown operator {op['name']}")


def decide(rec, n):
    """The exact row decision for n in the residual's slice."""
    return p699.row(n, rec["decide"]["args"]["i"])


def _next_i3(lo, count):
    heap = []
    a = 2
    while 2 ** a <= 64 * (lo + 1) ** 2 or a < 8:
        for eps in (0, 1):
            K = 2 ** (a - 1) * 3 ** eps
            A = max(1, (lo + 1 + 2 * K - 1) // (2 * K))
            A += 1 - A % 2
            got = 0
            while got < count:
                n = 2 * K * A
                L = (n - 1) * (n - 2)
                if 3 * L * L > 16 * K ** 6:
                    break
                if not (A % 3 == 0 and (eps == 1 or A % 9 != 0)):
                    heapq.heappush(heap, n)
                    got += 1
                A += 2
        a += 1
        if 2 ** a > (lo + 1) * 2 ** 64:
            break
    return sorted(set(heapq.nsmallest(count, heap)))


def frontier(rec, count=3):
    """The `count` least residual members above the searched bound: the first unsearched cases.

    Computed live for the i = 3 residual, whose members have a closed form. For the general
    residuals the ledger stores a sample found by the C engine (`frontier_sample`), because
    walking the progressions in Python near 10^15 is hopeless."""
    lo = bound(rec)
    if rec["operator"]["name"] == "p699.special_i3":
        return _next_i3(lo, count)
    return [int(x["n"]) for x in rec.get("frontier_sample", {}).get("members", [])][:count]
