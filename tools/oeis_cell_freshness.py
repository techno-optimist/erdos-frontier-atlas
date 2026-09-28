#!/usr/bin/env python3
"""Flag gap-map cells that the OEIS already covers.

  python3 tools/oeis_cell_freshness.py --seq-dir DIR            # read DIR/A######.seq
  python3 tools/oeis_cell_freshness.py --seq-dir DIR --fetch    # download missing records first

For every open atlas/gap_map.json row whose quantity starts with "A######(N)",
compare the cell index N with the OEIS record's extent: its data (offset plus
the number of terms, minus one) and any "Table of n, a(n) for n = X..Y" link.
A row whose N falls inside that extent is reported COVERED: the cell may have
been settled upstream since the row was written (the 2026-09-27 curation found
four such rows by hand: #156, #451, #1057, #1095).

Read-only: it prints a report and never edits the atlas. A flag is a lead, not
a verdict. Tables can carry placeholders for unknown entries (reported as
COVERED?), and a record can list bounds. Read the record, and the row's own
notes, before re-pointing a row.

--fetch reads https://raw.githubusercontent.com/oeis/oeisdata/main/seq/<A###>/<A######>.seq
(the OEIS data mirror, CC BY-SA 4.0); nothing is fetched otherwise.
"""
import argparse
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
MIRROR = "https://raw.githubusercontent.com/oeis/oeisdata/main/seq/{d}/{a}.seq"
PLACEHOLDER = re.compile(r"unknown|-1 for|not known|conjectur|incomplete", re.I)


def parse_seq(text, anum):
    """Offset, last index of the data section, and every 'Table of n, a(n) for n = X..Y' link."""
    def line(tag):
        m = re.search(rf"^%{tag} {anum} (.*)$", text, re.M)
        return m.group(1) if m else None
    off = line("O")
    offset = int(off.split(",")[0]) if off else 1
    terms = []
    for tag in ("S", "T", "U"):
        body = line(tag)
        if body:
            terms += [t for t in body.strip().rstrip(",").split(",") if t.strip()]
    tables = []
    for m in re.finditer(rf"^%H {anum} (.*)$", text, re.M):
        t = re.search(r"Table of n, a\(n\) for n\s*=\s*(-?\d+)\s*\.\.\s*(\d+)", m.group(1))
        if t:
            tables.append((int(t.group(1)), int(t.group(2)), bool(PLACEHOLDER.search(m.group(1)))))
    return {"offset": offset, "data_end": offset + len(terms) - 1, "tables": tables}


def cell_index(quantity, anum):
    m = re.match(rf"\s*{anum}\((\d+)\)", quantity)
    return int(m.group(1)) if m else None


def assess(n, info):
    """COVERED if a clean table or the data reaches n; COVERED? if only a table with
    placeholders does; open otherwise."""
    if n <= info["data_end"] or any(lo <= n <= hi and not ph for lo, hi, ph in info["tables"]):
        return "COVERED"
    if any(lo <= n <= hi for lo, hi, ph in info["tables"]):
        return "COVERED?"
    return "open"


def extent_text(info):
    tabs = ", ".join(f"table {lo}..{hi}" + (" (placeholders)" if ph else "")
                     for lo, hi, ph in info["tables"])
    return f"data ..{info['data_end']}" + (f"; {tabs}" if tabs else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq-dir", required=True)
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--gap-map", default=str(ROOT / "atlas" / "gap_map.json"))
    args = ap.parse_args()
    seq_dir = pathlib.Path(args.seq_dir)
    seq_dir.mkdir(parents=True, exist_ok=True)
    entries = json.loads(pathlib.Path(args.gap_map).read_text(encoding="utf-8"))["entries"]
    report, missing = [], []
    for e in entries:
        a = e.get("oeis")
        if e.get("status") != "open" or not a:
            continue
        n = cell_index(e["quantity"], a)
        if n is None:
            continue
        path = seq_dir / f"{a}.seq"
        if not path.exists() and args.fetch:
            with urllib.request.urlopen(MIRROR.format(d=a[:4], a=a), timeout=30) as r:
                path.write_bytes(r.read())
        if not path.exists():
            missing.append(a)
            continue
        info = parse_seq(path.read_text(encoding="utf-8", errors="replace"), a)
        report.append((assess(n, info), e["problem"], f"{a}({n})", extent_text(info)))
    order = {"COVERED": 0, "COVERED?": 1, "open": 2}
    for verdict, p, cell, ext in sorted(report, key=lambda r: (order[r[0]], r[1])):
        if verdict != "open":
            print(f"{verdict:<9} #{p:<5} {cell:<16} {ext}")
    counts = {k: sum(r[0] == k for r in report) for k in order}
    print(f"\n{len(report)} open cells checked: {counts['COVERED']} covered, "
          f"{counts['COVERED?']} covered only by a table with placeholders, {counts['open']} open"
          + (f"; {len(missing)} record(s) missing (use --fetch)" if missing else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
