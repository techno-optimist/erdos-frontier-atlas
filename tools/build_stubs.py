#!/usr/bin/env python3
"""build_stubs.py — compile the machine-readable Erdős hub index (Tier 1 stubs).

The hub is the AGENT-coordination annex to erdosproblems.com (Thomas Bloom's
canonical human index), NOT a mirror of it. This compiler is the whole
"complement-and-feed-back" stance made mechanical:

  * It ingests ONLY two Apache-2.0 sources, each attributed in NOTICE:
      A. teorth/erdosproblems  data/problems.yaml   (Bloom + Tao's sanctioned,
         machine-readable metadata: number, prize, status, oeis, tags, formalized)
      B. google-deepmind formal-conjectures ErdosProblems/*.lean docstrings
         (informal statements for the ~404 formalized problems)
  * It NEVER crawls or copies prose from erdosproblems.com. For the ~813 problems
    with no Lean docstring, `statement` stays null and the canonical prose lives
    at `erdos_url` — a LINK, not a copy. This firewall is enforced in code:
    the build HARD-FAILS if any statement_source=="link" stub carries prose.
  * It overlays our own deep records (atlas/problems.json) via `deep_ref`, so a
    stub is promoted in place when it earns a board_class / certificate.

Output: atlas/stubs.json — one sorted-by-id record per problem, a deterministic
rebuild artifact (re-run and diff), pinning the source commit SHAs.

Usage: python3 tools/build_stubs.py            # writes atlas/stubs.json
       python3 tools/build_stubs.py --check    # build in memory, assert, no write
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEORTH = Path(__file__).resolve().parents[2] / "teorth-erdosproblems"
FORMAL = Path(__file__).resolve().parents[2] / "formal-conjectures" / "FormalConjectures" / "ErdosProblems"
OUT = ROOT / "atlas" / "stubs.json"

CANONICAL_SOURCE = "erdosproblems.com — metadata mirror of the community database (link only, no prose copied)"

# teorth status.state -> (our status, upstream_status). Open-ish states stay
# open; everything resolved (proved/solved/disproved/independent/(Lean)) is
# solved upstream. Mirrors google-deepmind's own status reading.
OPEN_STATES = {"open", "falsifiable", "verifiable", "decidable"}


def _sha(repo: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def _yaml_load(path: Path):
    try:
        import yaml
        return yaml.safe_load(path.read_text())
    except ModuleNotFoundError:
        # tiny dependency-free fallback for this specific flat list-of-dicts file
        raise SystemExit("PyYAML required: pip install pyyaml")


def map_status(state: str):
    s = (state or "").strip()
    if s in OPEN_STATES:
        return "open", "Open"
    return "solved-upstream", "Solved"


def parse_lean(num: int, path: Path) -> dict:
    """Extract the informal statement + formal metadata for erdos_<num> from its
    Lean file. Statement = the /-- -/ docstring on the MAIN theorem (not a
    .variants). Returns {} if the file has no usable main-theorem docstring."""
    text = path.read_text(errors="replace")
    out = {"in_lean": True, "lean_path": str(path.relative_to(path.parents[3]))}
    # locate the MAIN declaration for this problem (not a .variants)
    m = re.search(r"(?:theorem|lemma|def|abbrev)\s+erdos_%d\b(?!\.)" % num, text)
    if m:
        pre = text[:m.start()]
        # the docstring belongs to this declaration iff only attribute lines /
        # whitespace sit between the docstring's closing -/ and the declaration
        close = pre.rfind("-/")
        if close != -1 and re.fullmatch(r"\s*(?:@\[[^\]]*\]\s*)*", pre[close + 2:]):
            openp = pre.rfind("/--", 0, close)
            if openp != -1:
                out["statement"] = re.sub(r"\s+", " ", pre[openp + 3:close]).strip()
        tail = pre[-400:]                       # attributes directly above the declaration
        cat = re.search(r"@\[category\s+([^,\]]+)", tail)
        if cat:
            out["formal_status"] = cat.group(1).strip()
        ams = re.search(r"\bAMS\s+([\d ]+)", tail)
        if ams:
            out["msc"] = ams.group(1).split()
    if not out.get("formal_status"):
        cat = re.search(r"@\[category\s+(research (?:open|solved))", text)
        out["formal_status"] = cat.group(1) if cat else None
    ans = re.search(r"answer\((True|False|sorry)\)", text)
    out["answer"] = ans.group(1) if ans else None
    return out


def build():
    teorth_yaml = TEORTH / "data" / "problems.yaml"
    problems = _yaml_load(teorth_yaml)
    teorth_sha, formal_sha = _sha(TEORTH), _sha(FORMAL)

    # deep-record overlay: id -> {p42_slug, beatable, board_class}
    deep = {}
    atlas = json.loads((ROOT / "atlas" / "problems.json").read_text())
    for p in atlas.get("problems", atlas):
        deep[p["id"]] = {"p42_slug": p.get("p42_slug"),
                         "beatable": p.get("beatable"),
                         "board_class": p.get("board_class")}

    lean_files = {int(f.stem): f for f in FORMAL.glob("*.lean") if f.stem.isdigit()}

    stubs = []
    for e in problems:
        num = int(e["number"])          # teorth stores number as a string; the key is the integer
        state = (e.get("status") or {}).get("state") if isinstance(e.get("status"), dict) else e.get("status")
        status, upstream = map_status(state)

        rec = {
            "id": num,
            "erdos_url": f"https://www.erdosproblems.com/{num}",
            "canonical_source": CANONICAL_SOURCE,
            "prize": e.get("prize"),
            "oeis": [x for x in (e.get("oeis") or []) if re.fullmatch(r"A\d{6}", str(x))],
            "tags": e.get("tags") or [],
            "upstream_state_raw": state,
            "upstream_status": upstream,
            "status": status,
            "statement_source": "link",
            "statement": None,
            "formalized": {"in_lean": False, "lean_path": None,
                           "formal_status": None, "answer": None},
            "msc": [],
            "deep_ref": None,
            "p42_slug": None,
            "provenance": {"sources": [
                {"repo": "teorth/erdosproblems", "file": "data/problems.yaml",
                 "commit": teorth_sha, "license": "Apache-2.0"}]},
        }

        # Pass B: Lean prose overlay (Apache-2.0 docstring) for formalized problems
        lf = lean_files.get(num)
        if lf:
            info = parse_lean(num, lf)
            rec["formalized"] = {
                "in_lean": True, "lean_path": info.get("lean_path"),
                "formal_status": info.get("formal_status"), "answer": info.get("answer")}
            if info.get("msc"):
                rec["msc"] = info["msc"]
            if info.get("statement"):
                rec["statement"] = info["statement"]
                rec["statement_source"] = "lean"
            rec["provenance"]["sources"].append(
                {"repo": "google-deepmind/formal-conjectures", "file": info.get("lean_path"),
                 "commit": formal_sha, "license": "Apache-2.0"})

        # Deep overlay: promote-in-place link to our audited record + status refine
        d = deep.get(num)
        if d:
            rec["deep_ref"] = f"atlas/problems.json#{num}"
            rec["p42_slug"] = d.get("p42_slug")
            if status != "solved-upstream":
                if d.get("beatable") == "MOVABLE":
                    rec["status"] = "movable"
                elif d.get("beatable") == "WALL":
                    rec["status"] = "wall"

        stubs.append(rec)

    stubs.sort(key=lambda r: r["id"])

    # LICENSING FIREWALL (code, not policy): a link-only stub must never carry prose.
    for r in stubs:
        if r["statement_source"] == "link" and r["statement"] is not None:
            raise SystemExit(f"FIREWALL VIOLATION: id {r['id']} is link-only but carries statement prose")
        if r["statement_source"] == "lean" and not r["formalized"]["in_lean"]:
            raise SystemExit(f"integrity: id {r['id']} statement_source=lean but not in_lean")

    doc = {
        "schema": "erdos-hub-stub-v1",
        "note": "Machine-readable agent-coordination index for the Erdős problems. "
                "Annex to erdosproblems.com (canonical human index); complements, never mirrors. "
                "Regenerate with tools/build_stubs.py; do not hand-edit.",
        "sources": [
            {"repo": "teorth/erdosproblems", "commit": teorth_sha, "license": "Apache-2.0",
             "attribution": "Erdős problems database contributors (T. Bloom, T. Tao, et al.)"},
            {"repo": "google-deepmind/formal-conjectures", "commit": formal_sha, "license": "Apache-2.0",
             "attribution": "The Formal Conjectures Authors"}],
        "counts": summarize(stubs),
        "problems": stubs,
    }
    return doc


def summarize(stubs):
    from collections import Counter
    by_status = Counter(r["status"] for r in stubs)
    return {
        "total": len(stubs),
        "by_status": dict(sorted(by_status.items())),
        "in_lean": sum(1 for r in stubs if r["formalized"]["in_lean"]),
        "with_statement": sum(1 for r in stubs if r["statement"]),
        "link_only": sum(1 for r in stubs if r["statement_source"] == "link"),
        "deep_records": sum(1 for r in stubs if r["deep_ref"]),
        "cash_prize": sum(1 for r in stubs if r["prize"] and r["prize"] != "no"),
    }


VIEW = ROOT / "views" / "index.md"


def write_view(doc):
    """Generate the human board from data. Shows the ACTIONABLE subset (audited
    deep records) richly; the full 1217 live in stubs.json — we do NOT dump 1217
    rows of mostly-untouched stubs (that is the vanity-dashboard trap)."""
    c = doc["counts"]
    titles = {}
    atlas = json.loads((ROOT / "atlas" / "problems.json").read_text())
    for p in atlas.get("problems", atlas):
        titles[p["id"]] = p.get("title", "")
    deep = [r for r in doc["problems"] if r["deep_ref"]]
    order = {"movable": 0, "in-progress": 1, "wall": 2, "solved": 3, "open": 4, "solved-upstream": 5, "stub": 6}
    deep.sort(key=lambda r: (order.get(r["status"], 9), r["id"]))
    L = []
    L.append("# The Erdős Frontier Atlas — hub index\n")
    L.append("*This file is generated by `tools/build_stubs.py`. Do not hand-edit; "
             "re-run the compiler and diff.*\n")
    L.append("The machine-readable **agent-coordination annex** to "
             "[erdosproblems.com](https://www.erdosproblems.com) (Thomas Bloom's canonical human "
             "index of the Erdős problems). It answers what that site structurally can't: for each "
             "problem, *what is its computational attack-state — movable, walled, or solved; is "
             "there a replayable certificate; is it P42-boardable?* It **complements, never mirrors**: "
             "prose is never copied from erdosproblems.com; every record links back to the canonical "
             "entry, and verified records flow back upstream.\n")
    L.append(f"**Sources** (Apache-2.0, see [`NOTICE`](../NOTICE)): "
             f"`teorth/erdosproblems` (Bloom + Tao) · `google-deepmind/formal-conjectures`. "
             f"Full machine index: [`atlas/stubs.json`](../atlas/stubs.json).\n")
    L.append("## Coverage\n")
    L.append(f"| total | movable | wall | open | solved-upstream | formalized (Lean) | with statement | audited (deep) | cash-prize |")
    L.append(f"|--:|--:|--:|--:|--:|--:|--:|--:|--:|")
    bs = c["by_status"]
    L.append(f"| **{c['total']}** | {bs.get('movable',0)} | {bs.get('wall',0)} | {bs.get('open',0)} "
             f"| {bs.get('solved-upstream',0)} | {c['in_lean']} | {c['with_statement']} | {c['deep_records']} | {c['cash_prize']} |\n")
    L.append("## Audited frontier (deep records)\n")
    L.append("The subset we have deep-audited — pinned verifier, current record, board class. "
             "Everything else is a machine stub in `stubs.json` linking to the canonical entry.\n")
    L.append("| # | problem | status | prize | upstream | links |")
    L.append("|--:|---|---|---|---|---|")
    for r in deep:
        i = r["id"]
        title = (titles.get(i, "") or "").replace("|", "\\|")[:70]
        prize = r["prize"] if r["prize"] and r["prize"] != "no" else "—"
        links = f"[erdos.com]({r['erdos_url']})"
        if r.get("p42_slug"):
            links += f" · P42:`{r['p42_slug']}`"
        L.append(f"| {i} | {title} | `{r['status']}` | {prize} | {r['upstream_status']} | {links} |")
    L.append("\n*Generated from data — counts are never hand-pinned. "
             "`status` reflects our compute triage; `upstream` reflects erdosproblems.com via the teorth spine.*\n")
    VIEW.parent.mkdir(exist_ok=True)
    VIEW.write_text("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="build + assert, do not write")
    args = ap.parse_args()
    doc = build()
    c = doc["counts"]
    # invariants (the rebuild-artifact contract)
    assert c["total"] == 1217, c["total"]
    assert c["link_only"] + c["with_statement"] == c["total"]
    assert c["in_lean"] >= 400, c["in_lean"]
    print(json.dumps(c, indent=1))
    if not args.check:
        OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
        write_view(doc)
        print(f"wrote {OUT} ({c['total']} problems) + {VIEW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
