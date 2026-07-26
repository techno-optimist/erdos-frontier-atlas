"""The triage is a screening result, and must not be read as a target list.

43 problems carry an upstream finite handle. Triaging them for reachability
returned 32 WALL, 5 MAYBE, 6 TARGET — roughly one workable lane in seven, which
is the number to remember before anyone points a farm at this file.

These checks pin the properties that make the artifact honest rather than
promotional: every entry carries a verdict and a reason, and a TARGET must name
the concrete witness, the smallest untested case, and a search-space estimate.
A "target" without those three is an aspiration.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = json.loads((ROOT / "atlas" / "finite_handle_triage.json").read_text(encoding="utf-8"))


def test_counts_match_the_entries():
    from collections import Counter
    got = Counter(e["verdict"] for e in DOC["entries"])
    for k in ("TARGET", "MAYBE", "WALL"):
        assert DOC["counts"][k] == got[k], f"{k}: stated {DOC['counts'][k]}, recomputed {got[k]}"
    assert DOC["counts"]["total"] == len(DOC["entries"])


def test_every_entry_has_a_reason():
    bad = [e["erdos_id"] for e in DOC["entries"] if not e.get("verdict_reason")]
    assert not bad, f"verdicts with no reason: {bad}"


def test_targets_are_specific():
    """A TARGET must be actionable, or it is an aspiration wearing a verdict."""
    vague = []
    for e in DOC["entries"]:
        if e["verdict"] != "TARGET":
            continue
        for field in ("what_a_witness_is", "smallest_untested_case", "search_space_estimate"):
            v = (e.get(field) or "").strip()
            if len(v) < 12 or v.upper() == "UNKNOWN":
                vague.append(f"#{e['erdos_id']}.{field}")
    assert not vague, (
        f"TARGET entries missing the fields that make them actionable: {vague}. "
        f"A target names the witness, the next case, and the search space.")


def test_the_triage_only_covers_finite_handled_problems():
    probs = json.loads((ROOT / "atlas" / "stubs.json").read_text(encoding="utf-8"))["problems"]
    handled = {p["id"] for p in probs if p.get("upstream_finite_handle")}
    stray = [e["erdos_id"] for e in DOC["entries"] if e["erdos_id"] not in handled]
    assert not stray, f"triage covers problems with no upstream finite handle: {stray}"


def test_walls_remain_the_majority_verdict():
    """If this ever flips, someone has started grading on enthusiasm."""
    assert DOC["counts"]["WALL"] > DOC["counts"]["TARGET"] + DOC["counts"]["MAYBE"], (
        "most finite-handled problems are walls; a triage that says otherwise needs "
        "re-reading before it is trusted")
