#!/usr/bin/env python3
"""Emit our 84-entry table in the RevLex-Index chirotope encoding used by the
Finschi-Fukuda database (and by Miyata-Moriyama-Fukuda's classification files),
so a human can look the object up in those catalogues directly.

RevLex-Index order of the r-subsets was read off the column header published at
https://finschi.com/math/om/?p=catom&card=9&rank=3&filter=nondeg :

    111211212311212312341121231234123451121231234123451234561121231234123451234561234567
    223323344423344455552334445555666662334445555666667777772334445555666667777778888888
    344455555566666666667777777777777778888888888888888888889999999999999999999999999999

i.e. subsets {a<b<c} of {1..9} sorted by (c, b, a) lexicographically.  This
script REDERIVES that order and asserts it reproduces the published header
verbatim, so the encoding is checked, not assumed.

Finschi labels elements 1..9; our table labels them 0..8 (element i <-> i+1).
"""

import itertools
import json

# `python3 -I` (isolated mode) implies -P, dropping this script's own directory from sys.path,
# so the sibling import below fails. Re-add it: keeps -I hermeticity AND makes the documented
# replay work. (Same fix as certificates/jc-family-fences -- this is a house convention.)
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))

from chirotope_axioms import CHI, SHA

HEADER = (
 "111211212311212312341121231234123451121231234123451234561121231234123451234561234567",
 "223323344423344455552334445555666662334445555666667777772334445555666667777778888888",
 "344455555566666666667777777777777778888888888888888888889999999999999999999999999999",
)


def revlex_subsets(n=9, r=3):
    """{a<b<c} sorted by (c,b,a) lexicographically."""
    return sorted(itertools.combinations(range(1, n + 1), r),
                  key=lambda s: tuple(reversed(s)))


def main():
    order = revlex_subsets()
    assert len(order) == 84
    rebuilt = tuple("".join(str(s[k]) for s in order) for k in range(3))
    assert rebuilt == HEADER, "derived RevLex order does not match published header"

    s = "".join("+" if CHI[tuple(x - 1 for x in sub)] > 0 else "-" for sub in order)
    # global reorientation freedom: chi and -chi are the same oriented matroid
    s_neg = "".join("-" if c == "+" else "+" for c in s)

    print(json.dumps({
        "revlex_order_matches_published_header": True,
        "payload_sha256": SHA,
        "n": 9, "rank": 3, "uniform": True,
        "revlex_index_chirotope_chi": s,
        "revlex_index_chirotope_minus_chi": s_neg,
        "note": ("Elements 1..9 in this encoding correspond to our labels 0..8. "
                 "This string is OUR labelling, not a canonical isomorphism-class "
                 "representative, so it need not equal Finschi's catalogue "
                 "representative for the class verbatim."),
    }, indent=2))
    print()
    print(HEADER[0]); print(HEADER[1]); print(HEADER[2]); print(s)


if __name__ == "__main__":
    main()
