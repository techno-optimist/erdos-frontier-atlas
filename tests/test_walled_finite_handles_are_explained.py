"""A problem that is both walled by us and finite-handled upstream must say why.

`upstream_finite_handle` marks the 43 problems erdosproblems.com calls
`decidable`, `falsifiable` or `verifiable`. It reads like a target list. Seven of
those are on our wall list, and six of the seven carry a prize — so they are
simultaneously the most inviting entries in the atlas and the ones where spending
compute is most certainly wasted.

The trap has a mechanism worth stating: a conjecture gets marked falsifiable
precisely when it is *believed true*, so the finite object it advertises is the
one nobody expects to exist. Several are additionally proved for all large n,
which turns "falsifiable" into "finitely many hard leftovers".

So the rule: if a problem carries a finite handle AND we call it a wall,
`atlas/walls.md` has to name it and explain why the handle does not help.
Otherwise the field is an invitation with no warning attached.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_every_walled_finite_handle_is_named_in_walls_md():
    probs = json.loads((ROOT / "atlas" / "stubs.json").read_text(encoding="utf-8"))["problems"]
    walls = (ROOT / "atlas" / "walls.md").read_text(encoding="utf-8")
    both = [p for p in probs
            if p.get("upstream_finite_handle") and p.get("status") == "wall"]
    assert both, "expected some problems to be both walled and finite-handled"
    unexplained = [p["id"] for p in both
                   if not re.search(rf"#\*{{0,2}}{p['id']}\*{{0,2}}\b", walls)]
    assert not unexplained, (
        f"these problems are walled by us AND carry an upstream finite handle, but "
        f"atlas/walls.md never names them: {unexplained}. Upstream's handle "
        f"classifies decidability in principle; the wall classifies reachability in "
        f"practice. Both can be true — but a reader who sees only the handle will "
        f"read a wall as a target, and most of these carry prizes.")


def test_the_orthogonality_warning_is_present():
    walls = (ROOT / "atlas" / "walls.md").read_text(encoding="utf-8")
    assert "upstream_finite_handle" in walls, (
        "atlas/walls.md must explain the finite-handle field, since that field "
        "makes several walls look like targets")
