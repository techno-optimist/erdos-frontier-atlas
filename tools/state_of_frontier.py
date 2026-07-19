#!/usr/bin/env python3
"""Generate views/state_of_frontier.md — the State of the Frontier report (WS1 / EFA-DR1).

Inputs (the only two):
  atlas/gap_map.json          the [L,U] ledger with evidence[] + confidence classes
  README.md                   the "CHRONOS Frontier Board" section (movement record)

The report is DETERMINISTIC: it contains no generation timestamp — every date in it
comes from the data (provenance/evidence dates, board 'when' column), so regenerating
from unchanged inputs yields byte-identical output. That is what makes `--check` a
meaningful staleness gate.

  python3 tools/state_of_frontier.py            # (re)write views/state_of_frontier.md
  python3 tools/state_of_frontier.py --check    # exit 1 if the committed view is stale
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAP_MAP = ROOT / "atlas" / "gap_map.json"
README = ROOT / "README.md"
OUT = ROOT / "views" / "state_of_frontier.md"

CLASS_MEANING = {
    "C0": "formal proof, machine-checked",
    "C1": "&ge;2 independent implementations or replays with distinct artifacts at the claimed range",
    "C2": "exactly one verified, replayable implementation",
    "C3": "literature- or numerics-grade — no independent in-project verification artifact",
}

KIND_MEANING = {
    "value_gap": "both bounds known; the open `[L, U]` gap is the object",
    "next_cell": "the next uncomputed term of a sequence or table",
    "verified_range": "a “no counterexample below N” frontier; `lower` records the verified-through value",
    "bounded_below_only": "one-sided bracket: only a lower bound is known",
    "bounded_above_only": "one-sided bracket: only an upper bound is known",
    "not_gap_shaped": "on the map for completeness; the problem has no `[L, U]` shape to work",
}
KIND_ORDER = ["value_gap", "next_cell", "verified_range",
              "bounded_below_only", "bounded_above_only", "not_gap_shaped"]

WORKABLE_FEAS = ("open-easy", "plausible")


def is_workable(entry):
    """The mechanical witness-workable filter (stated verbatim in the report):
    still open, has a witness-improvable side, and that side is feasibly workable."""
    return (entry["status"] == "open"
            and entry["witness_side"] != "none"
            and entry["witness_feasibility"] in WORKABLE_FEAS)


def md_escape(text, limit=None):
    """Make a data string safe inside a markdown table cell."""
    text = " ".join(str(text).split())          # collapse whitespace/newlines
    text = text.replace("|", "\\|")
    if limit is not None and len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def provenance_bucket(entry):
    added_by = entry["provenance"]["added_by"]
    if added_by.startswith("gap-map miner"):
        return "agent-mined"
    if "triage" in added_by:
        return "curated seed"
    return "lane-added"


def data_high_watermark(entries):
    dates = []
    for e in entries:
        dates.append(e["provenance"]["date"])
        for item in e.get("evidence", []):
            dates.append(item["date"])
    return max(dates)


def parse_board_rows(readme_text):
    """Rows of the first markdown table under '## CHRONOS Frontier Board'."""
    lines = readme_text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines)
                     if ln.strip() == "## CHRONOS Frontier Board")
    except StopIteration:
        raise SystemExit("state_of_frontier: README has no '## CHRONOS Frontier Board' section")
    rows, in_table = [], False
    for ln in lines[start + 1:]:
        if ln.startswith("## "):                # next section — stop
            break
        stripped = ln.strip()
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue                        # separator row
            if not in_table:                    # header row
                in_table = True
                continue
            if len(cells) >= 5:
                rows.append(cells[:5])
        elif in_table:
            break                               # table ended
    if not rows:
        raise SystemExit("state_of_frontier: no rows parsed from the Frontier Board table")
    return rows


def generate():
    gm = json.loads(GAP_MAP.read_text(encoding="utf-8"))
    entries = gm["entries"]
    board_rows = parse_board_rows(README.read_text(encoding="utf-8"))

    total = len(entries)
    prov_counts, class_counts, kind_counts, kind_workable = {}, {}, {}, {}
    for e in entries:
        prov_counts[provenance_bucket(e)] = prov_counts.get(provenance_bucket(e), 0) + 1
        class_counts[e["confidence"]] = class_counts.get(e["confidence"], 0) + 1
        kind_counts[e["kind"]] = kind_counts.get(e["kind"], 0) + 1
        if is_workable(e):
            kind_workable[e["kind"]] = kind_workable.get(e["kind"], 0) + 1
    workable = sorted((e for e in entries if is_workable(e)),
                      key=lambda e: (WORKABLE_FEAS.index(e["witness_feasibility"]),
                                     e["problem"], e["quantity"]))

    tier_counts = {}
    for row in board_rows:
        tier = row[0]
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    L = []
    w = L.append
    w("# State of the Frontier — EFA-DR1")
    w("")
    w("> Generated by [`tools/state_of_frontier.py`](../tools/state_of_frontier.py) from")
    w("> [`atlas/gap_map.json`](../atlas/gap_map.json) and the README")
    w("> [Frontier Board](../README.md#chronos-frontier-board). Do not edit by hand —")
    w("> regenerate with `make state-of-frontier`; `make check-views` fails if this file")
    w("> is stale. Deterministic: no generation timestamp — every date below comes from")
    w(f"> the data. **Data through {data_high_watermark(entries)}** (latest provenance/evidence date).")
    w("")
    w("The gap map is the versioned `[L, U]` ledger over bounded quantities of open")
    w("problems (charter Tenet 2: the bracket is the unit of progress). This report is")
    w("the release-facing summary of its current state.")
    w("")

    w("## The ledger at a glance")
    w("")
    w(f"- **{total} bounded quantities** across the Erdős-hub problems.")
    prov_bits = ", ".join(f"**{prov_counts[k]}** {k}" for k in
                          ("curated seed", "lane-added", "agent-mined") if k in prov_counts)
    w(f"- Provenance (mechanical, from `provenance.added_by`): {prov_bits}.")
    w("- Honest label: the agent-mined entries are structurally validated but **not yet")
    w("  independently number-re-verified** — they carry literature-grade evidence and")
    w("  therefore class C3 until a verification artifact exists (the WS1 release gate")
    w("  is exactly this labeling, not a claim of verification).")
    w("")

    w("## Confidence classes (the epistemic ledger)")
    w("")
    w("Every entry carries `evidence[]`; its class is **computed from that evidence** by")
    w("[`tools/validate_gap_map.py`](../tools/validate_gap_map.py), never asserted — the")
    w("validator fails any stored class the recorded evidence does not prove.")
    w("")
    w("| class | meaning | entries |")
    w("|---|---|---|")
    for cls in ("C0", "C1", "C2", "C3"):
        w(f"| {cls} | {CLASS_MEANING[cls]} | {class_counts.get(cls, 0)} |")
    w("")

    w("## Entries by kind")
    w("")
    w("| kind | meaning | entries | witness-workable |")
    w("|---|---|---|---|")
    for kind in KIND_ORDER:
        w(f"| `{kind}` | {KIND_MEANING[kind]} | {kind_counts.get(kind, 0)} "
          f"| {kind_workable.get(kind, 0)} |")
    w("")

    w(f"## Witness-workable quantities ({len(workable)})")
    w("")
    w("The mechanical filter: `status == \"open\"` **and** `witness_side != \"none\"`")
    w("**and** `witness_feasibility` ∈ {`open-easy`, `plausible`} — quantities where a")
    w("single submitted construction, checked by the entry's stated verifier, moves the")
    w("bracket. Sorted easiest-first, then by problem number. Bounds are shown")
    w("truncated — the full values, sources, and verifier specs live in")
    w("[`atlas/gap_map.json`](../atlas/gap_map.json).")
    w("")
    w("| problem | OEIS | quantity | side | feasibility | lower | upper |")
    w("|---|---|---|---|---|---|---|")
    for e in workable:
        oeis = f"[{e['oeis']}](https://oeis.org/{e['oeis']})" if e["oeis"] else "—"
        lo = md_escape(e["lower"]["value"], 60) if e["lower"] else "?"
        up = md_escape(e["upper"]["value"], 60) if e["upper"] else "?"
        w(f"| [#{e['problem']}](https://www.erdosproblems.com/{e['problem']}) "
          f"| {oeis} | {md_escape(e['quantity'], 110)} | {e['witness_side']} "
          f"| {e['witness_feasibility']} | {lo} | {up} |")
    w("")

    w("## Movement record (from the Frontier Board)")
    w("")
    w(f"{len(board_rows)} movements recorded on the")
    w("[CHRONOS Frontier Board](../README.md#chronos-frontier-board)"
      + " (" + " · ".join(f"{t} {n}" for t, n in sorted(tier_counts.items(),
                                                             key=lambda kv: -kv[1])) + ").")
    w("Corrected claims stay on the board by design (charter Tenet 5).")
    w("")
    w("| tier | problem | movement | certificate | when |")
    w("|---|---|---|---|---|")
    for row in board_rows:
        w("| " + " | ".join(row) + " |")
    w("")
    w("(Certificate links in this table are relative to the repository root, as in the")
    w("README.)")
    w("")

    w("## Movement changelog (DR1 baseline)")
    w("")
    w("**EFA-DR1 is the baseline release: there is no earlier data release to diff**")
    w("**against, so this changelog is a stub by construction.** From DR2 onward this")
    w("section is generated as the mechanical bracket-diff against the previous")
    w("release, one row per moved entry:")
    w("")
    w("| problem | quantity | bracket at DR(n−1) | bracket at DR(n) | class then → now | certificate |")
    w("|---|---|---|---|---|---|")
    w("| *(none — DR1 is the baseline)* | | | | | |")
    w("")
    w("A row qualifies only when the movement is backed by a replayable artifact")
    w("recorded in the entry's `evidence[]`; class regressions (e.g. a retraction")
    w("demoting C1 → C3) are listed in the same table, not hidden.")
    w("")

    w("## Reproduce")
    w("")
    w("```sh")
    w("make hello-frontier          # the 10-minute quickstart (git + cc + python3)")
    w("python3 tools/validate_gap_map.py    # structural + epistemic-ledger validation")
    w("make state-of-frontier       # regenerate this report from the data")
    w("make check-views             # fail if this report is stale")
    w("```")
    return "\n".join(L) + "\n"


def main():
    report = generate()
    if "--check" in sys.argv[1:]:
        on_disk = OUT.read_text(encoding="utf-8") if OUT.exists() else None
        if on_disk != report:
            print(f"STALE: {OUT.relative_to(ROOT)} does not match a regeneration from "
                  f"the data — run: make state-of-frontier")
            return 1
        print(f"OK: {OUT.relative_to(ROOT)} is current with the data")
        return 0
    OUT.write_text(report, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(report.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
