#!/usr/bin/env python3
"""Build book/BOOK.md — "Cartography of Numbers", the living book of the
frontier-cartography field (single-file seed edition).

A living book: prose sections are hand-written in book/chapters/*.md; every
table, count, and figure is GENERATED at build time from the repository's
ledgers and goes stale loudly (`make check-book` fails if BOOK.md no longer
matches a regeneration from the data). When the frontier moves, the book moves.

Chapter templates may contain generator directives as fenced blocks:

    ```efa:table gap_map_summary
    ```

The whole fenced block is replaced by markdown generated from the live data.
Available directives:

    edition_state      the seed edition's data high-watermark (preface)
    gap_map_summary    ledger totals, provenance, kinds, class distribution
    confidence_ledger  the C0–C3 table with computed entry counts
    board              the CHRONOS Frontier Board movement record (from README)
    fence_13           the Erdős #13 fence table from its certificate JSON
    shortlist          the WS4 effectivization shortlist, alive and dead
    observatory_curve  the R(3,k) emitted-size points + the mandatory
                       emitted-vs-minimal caveat (from observatory data)
    walls_summary      attack-state distribution: what is walled vs workable

The build is DETERMINISTIC: no timestamps — every date in the output comes from
the data, so regenerating from unchanged inputs yields byte-identical output.
That is what makes `--check` a meaningful staleness gate.

  python3 book/build_book.py            # (re)write book/BOOK.md
  python3 book/build_book.py --check    # exit 1 if BOOK.md is stale vs the data
  python3 book/build_book.py --root D   # operate on a repo copy rooted at D
"""
import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent

DIRECTIVE_OPEN = re.compile(r"^```efa:table\s+([a-z0-9_]+)\s*$")

HEADER = (
    "<!-- GENERATED FILE — do not edit. Edit book/chapters/*.md and run\n"
    "     `make book`; `make check-book` fails when this file is stale. -->\n"
)

CLASS_MEANING = {
    "C0": "formal proof, machine-checked",
    "C1": "&ge;2 independent implementations or replays with distinct artifacts at the claimed range",
    "C2": "exactly one verified, replayable implementation",
    "C3": "literature- or numerics-grade — no independent in-project verification artifact",
}

KIND_ORDER = ["value_gap", "next_cell", "verified_range",
              "bounded_below_only", "bounded_above_only", "not_gap_shaped"]

FEAS_ORDER = ["cell", "drat-candidate", "unknown", "wall"]
FEAS_MEANING = {
    "cell": "an uncomputed exact cell current exact tools can plausibly settle",
    "drat-candidate": "exact settlement looks reachable via a certified-UNSAT (DRAT) route",
    "unknown": "attack-state not yet priced",
    "wall": "the exact value needs an infeasible nonexistence proof — do not spend search compute here",
}

WORKABLE_FEAS = ("open-easy", "plausible")


def md_escape(text, limit=None):
    text = " ".join(str(text).split())
    text = text.replace("|", "\\|")
    if limit is not None and len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def is_workable(entry):
    return (entry["status"] == "open"
            and entry["witness_side"] != "none"
            and entry["witness_feasibility"] in WORKABLE_FEAS)


def data_high_watermark(entries):
    dates = []
    for e in entries:
        dates.append(e["provenance"]["date"])
        for item in e.get("evidence", []):
            dates.append(item["date"])
    return max(dates)


def parse_board_rows(readme_text):
    """Rows of the first markdown table under '## CHRONOS Frontier Board'
    (same contract as tools/state_of_frontier.py)."""
    lines = readme_text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines)
                     if ln.strip() == "## CHRONOS Frontier Board")
    except StopIteration:
        raise SystemExit("build_book: README has no '## CHRONOS Frontier Board' section")
    rows, in_table = [], False
    for ln in lines[start + 1:]:
        if ln.startswith("## "):
            break
        stripped = ln.strip()
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells):
                continue
            if not in_table:
                in_table = True
                continue
            if len(cells) >= 5:
                rows.append(cells[:5])
        elif in_table:
            break
    if not rows:
        raise SystemExit("build_book: no rows parsed from the Frontier Board table")
    return rows


class Book:
    """Loads the ledgers once; each gen_* method renders one directive."""

    def __init__(self, root: Path):
        self.root = root
        self.gap_map = json.loads((root / "atlas" / "gap_map.json").read_text(encoding="utf-8"))
        self.entries = self.gap_map["entries"]
        self.shortlist = json.loads(
            (root / "atlas" / "effectivization_shortlist.json").read_text(encoding="utf-8"))
        self.fence13 = json.loads(
            (root / "certificates" / "erdos-13" / "table.json").read_text(encoding="utf-8"))
        self.observatory = json.loads(
            (root / "observatory" / "measurements.json").read_text(encoding="utf-8"))
        self.board_rows = parse_board_rows((root / "README.md").read_text(encoding="utf-8"))

    # ---------------------------------------------------------------- edition
    def gen_edition_state(self):
        entries = self.entries
        classes = {}
        for e in entries:
            classes[e["confidence"]] = classes.get(e["confidence"], 0) + 1
        class_line = " · ".join(f"{c} {classes.get(c, 0)}" for c in ("C0", "C1", "C2", "C3"))
        tiers = {}
        for row in self.board_rows:
            tiers[row[0]] = tiers.get(row[0], 0) + 1
        tier_line = " · ".join(f"{t} {n}" for t, n in
                               sorted(tiers.items(), key=lambda kv: (-kv[1], kv[0])))
        return [
            "| this edition | state |",
            "|---|---|",
            f"| data through | **{data_high_watermark(entries)}** (latest provenance/evidence date in the gap map) |",
            f"| the ledger | **{len(entries)}** bounded quantities |",
            f"| confidence | {class_line} |",
            f"| movements on the board | **{len(self.board_rows)}** ({tier_line}) — corrected claims kept visible |",
        ]

    # ---------------------------------------------------------- gap_map_summary
    def gen_gap_map_summary(self):
        entries = self.entries
        prov, classes, kinds, kinds_workable = {}, {}, {}, {}
        for e in entries:
            added_by = e["provenance"]["added_by"]
            if added_by.startswith("gap-map miner"):
                bucket = "agent-mined"
            elif "triage" in added_by:
                bucket = "curated seed"
            else:
                bucket = "lane-added"
            prov[bucket] = prov.get(bucket, 0) + 1
            classes[e["confidence"]] = classes.get(e["confidence"], 0) + 1
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
            if is_workable(e):
                kinds_workable[e["kind"]] = kinds_workable.get(e["kind"], 0) + 1
        workable = sum(kinds_workable.values())
        prov_bits = ", ".join(f"**{prov[k]}** {k}" for k in
                              ("curated seed", "lane-added", "agent-mined") if k in prov)
        class_line = " · ".join(f"**{c}** {classes.get(c, 0)}" for c in ("C0", "C1", "C2", "C3"))
        L = [
            f"- **{len(entries)} bounded quantities** on the map "
            f"([`atlas/gap_map.json`](../atlas/gap_map.json)).",
            f"- Provenance (mechanical, from `provenance.added_by`): {prov_bits}.",
            f"- Confidence distribution (computed from `evidence[]`, never asserted): {class_line}.",
            f"- **{workable} witness-workable**: still open, with a side a single submitted",
            "  construction — checked by the entry's stated verifier — can move.",
            "",
            "| kind | entries | witness-workable |",
            "|---|---|---|",
        ]
        for kind in KIND_ORDER:
            L.append(f"| `{kind}` | {kinds.get(kind, 0)} | {kinds_workable.get(kind, 0)} |")
        return L

    # ------------------------------------------------------ confidence_ledger
    def gen_confidence_ledger(self):
        classes = {}
        for e in self.entries:
            classes[e["confidence"]] = classes.get(e["confidence"], 0) + 1
        L = [
            "Classes are computed from recorded `evidence[]` by",
            "[`tools/validate_gap_map.py`](../tools/validate_gap_map.py) — the validator",
            "fails any stored class the recorded evidence does not prove.",
            "",
            "| class | meaning | entries |",
            "|---|---|---|",
        ]
        for cls in ("C0", "C1", "C2", "C3"):
            L.append(f"| {cls} | {CLASS_MEANING[cls]} | {classes.get(cls, 0)} |")
        return L

    # ------------------------------------------------------------------ board
    def gen_board(self):
        tiers = {}
        for row in self.board_rows:
            tiers[row[0]] = tiers.get(row[0], 0) + 1
        tier_line = " · ".join(f"{t} {n}" for t, n in
                               sorted(tiers.items(), key=lambda kv: (-kv[1], kv[0])))
        L = [
            f"{len(self.board_rows)} movements recorded on the",
            "[CHRONOS Frontier Board](../README.md#chronos-frontier-board)"
            f" ({tier_line}).",
            "Corrected claims stay on the board by design (charter Tenet 5).",
            "",
            "| tier | problem | movement | certificate | when |",
            "|---|---|---|---|---|",
        ]
        for row in self.board_rows:
            L.append("| " + " | ".join(row) + " |")
        L += [
            "",
            "(Certificate links in this table are relative to the repository root,",
            "as on the board itself.)",
        ]
        return L

    # --------------------------------------------------------------- fence_13
    def gen_fence_13(self):
        t = self.fence13
        n_max = t["n_max"]
        f = t["f"]
        exceptions = {int(k): v for k, v in
                      t["exceptions_over_floor_n_over_3_plus_1"].items()}
        last_exc = max(exceptions)
        # Generator-side re-check: every N past the last exception must sit on
        # the bound, and every listed exception must actually exceed it.
        for n in range(1, n_max + 1):
            bound = n // 3 + 1
            if n in exceptions and not f[n - 1] > bound:
                raise SystemExit(f"fence_13: N={n} listed as exception but f<=bound")
            if n not in exceptions and n > last_exc and f[n - 1] != bound:
                raise SystemExit(f"fence_13: N={n} off the bound past the last exception")
        vals = ", ".join(str(v) for v in f)
        L = [
            f"Computed range: `N = 1…{n_max}` "
            "([`certificates/erdos-13/table.json`](../certificates/erdos-13/table.json);"
            " replay: `python3 certificates/erdos-13/verify.py`).",
            "",
            f"```",
            f"f(1..{n_max}) = {vals}",
            f"```",
            "",
            f"The bound `⌊N/3⌋ + 1` (Bedert's theorem, ineffective threshold) is exceeded",
            f"at exactly **{len(exceptions)}** values of N in the computed range:",
            "",
            "| N | f(N) | ⌊N/3⌋+1 | extremal witness |",
            "|---|---|---|---|",
        ]
        for n in sorted(exceptions):
            e = exceptions[n]
            wit = "{" + ", ".join(str(x) for x in e["witness"]) + "}"
            L.append(f"| {n} | {e['f']} | {e['bound']} | `{wit}` |")
        L += [
            "",
            f"**N = {last_exc} is the last exception in the computed range**: "
            f"`f(N) = ⌊N/3⌋ + 1` for every `{last_exc + 1} ≤ N ≤ {n_max}`. Because the",
            "theorem's threshold is ineffective, sporadic exceptions at larger N are",
            "**not excluded** — this is a lower fence on the threshold, not its location.",
        ]
        return L

    # -------------------------------------------------------------- shortlist
    def gen_shortlist(self):
        sl = self.shortlist
        alive = sl["plausible"]
        dead = sl["dead_do_not_rehunt"]
        L = [
            f"The WS4 hunt ([`atlas/effectivization_shortlist.json`]"
            "(../atlas/effectivization_shortlist.json)): "
            f"**{len(alive)} candidates alive, {len(dead)} dead** — the dead are kept",
            "so no one re-hunts them.",
            "",
            f"> {md_escape(sl['status_note'])}",
            "",
            "**Alive (graded, effectivization-checked):**",
            "",
            "| candidate | grade |",
            "|---|---|",
        ]
        for c in alive:
            L.append(f"| {md_escape(c['name'], 140)} | {c['grade']} |")
        L += [
            "",
            "**Dead — do not re-hunt (each with the specific reason recorded):**",
            "",
            "| candidate | why it is dead |",
            "|---|---|",
        ]
        for c in dead:
            L.append(f"| {md_escape(c['name'], 110)} | {md_escape(c['effectivization_check'], 190)} |")
        return L

    # ------------------------------------------------------ observatory_curve
    def gen_observatory_curve(self):
        obs = self.observatory
        order_label = {p: ("interleaved" if p.endswith("interleaved") else "lex")
                       for p in obs["pipelines"]}

        def fmt_bytes(n):
            return f"{n:,}"

        L = [
            f"> {md_escape(obs['caveat_emitted_vs_minimal'])}",
            "",
            f"Family: {md_escape(obs['family'])}",
            "",
            f"Completed family points: **{obs['family_points_completed']}** of "
            f"{obs['family_points_attempted']} attempted. Raw records with commands and",
            "sha256s: [`observatory/measurements.json`](../observatory/measurements.json);",
            "pinned pipelines: [`observatory/pipeline.json`](../observatory/pipeline.json).",
            "",
            "| family point | n | order | seed | emitted DRAT bytes | result |",
            "|---|---|---|---|---|---|",
        ]
        for m in obs["measurements"]:
            order = order_label.get(m["pipeline_id"], m["pipeline_id"])
            seed = m.get("seed", "—")
            result = m["result"]
            if result == "VERIFIED":
                size = fmt_bytes(m.get("emitted_drat_bytes", m.get("emitted_bytes")))
                res = "`s VERIFIED`"
                if "machine" in m:
                    res += f" — {m['machine'].split()[0]} (separate series)"
            elif result == "DNF_PROOF_SIZE_CAP":
                size = f"> {fmt_bytes(m['emitted_bytes_at_abort'])} at abort"
                res = "DNF at proof-size cap (later shown a **cap artifact** — superseded)"
            elif result == "ABORTED_OPERATOR":
                size = "—"
                res = "aborted by the operator (shared-host protection) — no datum"
            else:
                size = "—"
                res = md_escape(result)
            n_field = m["n"]
            L.append(f"| {m['family_point']} | {n_field} | {order} | {seed} | {size} | {res} |")
        fit = obs.get("growth_fit")
        L += [
            "",
            f"**Growth fit claimed: {'none' if fit is None else md_escape(fit)}.**",
            f"{md_escape(obs['growth_fit_note'])}",
        ]
        return L

    # ---------------------------------------------------------- walls_summary
    def gen_walls_summary(self):
        feas = {}
        for e in self.entries:
            k = e.get("exact_feasibility", "unknown")
            feas[k] = feas.get(k, 0) + 1
        workable = sum(1 for e in self.entries if is_workable(e))
        L = [
            "Exact-value attack-state over the gap map's "
            f"{len(self.entries)} quantities (field `exact_feasibility`):",
            "",
            "| attack-state | meaning | entries |",
            "|---|---|---|",
        ]
        for k in FEAS_ORDER:
            L.append(f"| `{k}` | {FEAS_MEANING[k]} | {feas.get(k, 0)} |")
        extra = sorted(set(feas) - set(FEAS_ORDER))
        for k in extra:
            L.append(f"| `{k}` | (unclassified value — fix the data) | {feas[k]} |")
        L += [
            "",
            f"Against that: **{workable}** quantities remain witness-workable — the",
            "honest territory *around* the walls. The named do-not-enter list, with the",
            "specific reason and source for each wall, is",
            "[`atlas/walls.md`](../atlas/walls.md).",
        ]
        return L

    # ------------------------------------------------------------- dispatcher
    def render_directive(self, name):
        fn = getattr(self, f"gen_{name}", None)
        if fn is None:
            raise SystemExit(f"build_book: unknown generator directive '{name}'")
        return fn()

    def expand_chapter(self, text, chapter_name):
        out, i = [], 0
        lines = text.splitlines()
        while i < len(lines):
            m = DIRECTIVE_OPEN.match(lines[i])
            if not m:
                out.append(lines[i])
                i += 1
                continue
            name = m.group(1)
            i += 1
            while i < len(lines) and lines[i].strip() != "```":
                i += 1
            if i >= len(lines):
                raise SystemExit(
                    f"build_book: unterminated efa:table block in {chapter_name}")
            i += 1                                      # skip closing fence
            out.extend(self.render_directive(name))
        return out

    def generate(self):
        chapters_dir = self.root / "book" / "chapters"
        chapter_files = sorted(chapters_dir.glob("*.md"))
        if not chapter_files:
            raise SystemExit(f"build_book: no chapters found in {chapters_dir}")
        parts = [HEADER]
        for i, path in enumerate(chapter_files):
            body = self.expand_chapter(path.read_text(encoding="utf-8"), path.name)
            while body and not body[-1].strip():
                body.pop()
            parts.append("\n".join(body) + "\n")
            if i < len(chapter_files) - 1:
                parts.append("\n---\n\n")
        return "".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if book/BOOK.md is stale vs the data")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                    help="repository root (default: this file's grandparent)")
    args = ap.parse_args()
    root = args.root.resolve()
    out = root / "book" / "BOOK.md"

    book = Book(root).generate()
    if args.check:
        on_disk = out.read_text(encoding="utf-8") if out.exists() else None
        if on_disk != book:
            print("STALE: book/BOOK.md does not match a regeneration from the "
                  "data — run: make book")
            return 1
        print("OK: book/BOOK.md is current with the data")
        return 0
    out.write_text(book, encoding="utf-8")
    print(f"wrote {out.relative_to(root)} ({len(book.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
