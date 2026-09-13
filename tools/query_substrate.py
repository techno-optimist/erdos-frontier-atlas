#!/usr/bin/env python3
"""Query the method substrate against the attack graph (stdlib, read-only).

  python3 tools/query_substrate.py methods
  python3 tools/query_substrate.py for 699
  python3 tools/query_substrate.py open
  python3 tools/query_substrate.py board

Does not write atlas/stubs.json or atlas/graph/. A candidate match is not
an implication and never sets a status.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_json(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def load_substrate():
    return load_json("atlas/substrate.json")


def load_stubs():
    return {p["id"]: p for p in load_json("atlas/stubs.json")["problems"]}


def load_graph():
    path = ROOT / "atlas" / "graph" / "graph.json"
    if not path.exists():
        return {"nodes": [], "edges": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _tags(stub):
    return set(stub.get("tags") or [])


def _oeis(stub):
    return set(stub.get("oeis") or [])


def selector_match(method, stub):
    sel = method.get("selectors") or {}
    if sel.get("ids") and stub["id"] in sel["ids"]:
        return True
    tags = _tags(stub)
    oeis = _oeis(stub)
    if sel.get("tags_all") and not set(sel["tags_all"]) <= tags:
        return False
    if sel.get("tags_any") and not (set(sel["tags_any"]) & tags):
        return False
    if sel.get("oeis_any"):
        if not (set(sel["oeis_any"]) & oeis):
            return False
        return True
    if sel.get("tags_all") or sel.get("tags_any"):
        return True
    return False


def applications_for(pid):
    sub = load_substrate()
    stubs = load_stubs()
    stub = stubs.get(int(pid))
    hits = []
    for method in sub["methods"]:
        for rel_name in ("discharges", "obstructions"):
            for rec in method.get(rel_name) or []:
                if rec["problem"] == int(pid):
                    hits.append({
                        "method": method["id"],
                        "status": method["status"],
                        "relation": rel_name,
                        "note": rec.get("note", ""),
                        "statement": method["statement"],
                        "remaining": method.get("remaining") or [],
                        "artifacts": method.get("artifacts") or [],
                    })
        if stub is not None and selector_match(method, stub):
            already = any(h["method"] == method["id"] for h in hits)
            if not already:
                hits.append({
                    "method": method["id"],
                    "status": method["status"],
                    "relation": "candidate",
                    "note": "tag/OEIS shape match only; not an implication",
                    "statement": method["statement"],
                    "remaining": method.get("remaining") or [],
                    "artifacts": method.get("artifacts") or [],
                })
    order = {"discharges": 0, "obstructions": 1, "candidate": 2}
    hits.sort(key=lambda h: (order[h["relation"]], h["method"]))
    return hits


def graph_context(pid):
    graph = load_graph()
    pid_s = f"P{int(pid)}"
    families = []
    neighbors = []
    for e in graph.get("edges") or []:
        if e.get("type") == "same_family" and pid_s in (e["src"], e["dst"]):
            other = e["dst"] if e["src"] == pid_s else e["src"]
            families.append({
                "other": other,
                "shared": e.get("shared") or [],
            })
        elif pid_s in (e.get("src"), e.get("dst")):
            neighbors.append(e)
    return families, neighbors


def render_for(pid):
    pid = int(pid)
    stubs = load_stubs()
    stub = stubs.get(pid)
    lines = [f"# Substrate for #{pid}"]
    if stub is None:
        lines.append("unknown problem id in atlas/stubs.json")
        return "\n".join(lines) + "\n"
    lines.append(
        f"status={stub['status']}  upstream={stub['upstream_status']}  "
        f"tags={', '.join(stub.get('tags') or []) or '—'}"
    )
    oeis = stub.get("oeis") or []
    if oeis:
        lines.append("oeis=" + ", ".join(oeis))
    families, _ = graph_context(pid)
    if families:
        for fam in families:
            lines.append(
                f"graph family {fam['other']} shares {', '.join(fam['shared'])}"
            )
    else:
        lines.append("no shared-OEIS family in the attack graph")
    hits = applications_for(pid)
    if not hits:
        lines.append("no substrate method matches")
        return "\n".join(lines) + "\n"
    for h in hits:
        lines.append("")
        lines.append(f"[{h['relation']}] {h['method']}  ({h['status']})")
        lines.append(h["statement"])
        if h["note"]:
            lines.append("note: " + h["note"])
        if h["remaining"]:
            lines.append("remaining: " + "; ".join(h["remaining"]))
    if pid == 699:
        lines.append("")
        lines.append("does not close P699")
        lines.append("not a solution of #699")
    return "\n".join(lines) + "\n"


def _open_status(stub):
    return stub["status"] in ("open", "movable")


def render_open():
    stubs = load_stubs()
    sub = load_substrate()
    lines = [
        "Method substrate — open/movable problems only.",
        "A CANDIDATE match is not an implication.",
        "",
        "DISCHARGE / OBSTRUCTION (reviewed or kernel-checked on that problem)",
    ]
    seen_d = []
    seen_c = []
    for method in sub["methods"]:
        for rec in method.get("discharges") or []:
            stub = stubs.get(rec["problem"])
            if stub and _open_status(stub):
                seen_d.append((method["id"], rec["problem"], "DISCHARGE", rec.get("note", "")))
        for rec in method.get("obstructions") or []:
            stub = stubs.get(rec["problem"])
            if stub and _open_status(stub):
                seen_d.append((method["id"], rec["problem"], "OBSTRUCTION", rec.get("note", "")))
        for stub in stubs.values():
            if not _open_status(stub):
                continue
            if not selector_match(method, stub):
                continue
            if any(rec["problem"] == stub["id"]
                   for rec in (method.get("discharges") or []) + (method.get("obstructions") or [])):
                continue
            seen_c.append((method["id"], stub["id"], "CANDIDATE",
                           "tag/OEIS shape match only; not an implication"))
    for row in sorted(seen_d, key=lambda r: (r[1], r[0])):
        lines.append(f"  #{row[1]:<5} {row[2]:<12} {row[0]}  {row[3]}")
    lines.append("")
    lines.append("CANDIDATE (tag/OEIS shape match only; not an implication)")
    for row in sorted(seen_c, key=lambda r: (r[1], r[0])):
        lines.append(f"  #{row[1]:<5} {row[2]:<12} {row[0]}  {row[3]}")
    lines.append("")
    lines.append(f"{len(seen_d)} discharge/obstruction rows, {len(seen_c)} candidate rows.")
    return "\n".join(lines) + "\n"


def render_methods():
    sub = load_substrate()
    lines = [sub["purpose"], ""]
    for m in sub["methods"]:
        d = [str(r["problem"]) for r in m.get("discharges") or []]
        lines.append(f"{m['id']}  [{m['status']}]  discharges #{', #'.join(d) if d else '—'}")
        lines.append("  " + m["statement"])
    return "\n".join(lines) + "\n"


def render_board():
    return (
        "# Method substrate\n\n"
        + load_substrate()["trust"] + "\n\n"
        + render_open()
    )


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in {
            "methods", "for", "open", "board"}:
        print(__doc__.strip())
        raise SystemExit(2)
    cmd = sys.argv[1]
    if cmd == "methods":
        print(render_methods(), end="")
    elif cmd == "for":
        if len(sys.argv) < 3:
            print("for: expected a problem id, e.g. `python3 tools/query_substrate.py for 699`")
            raise SystemExit(2)
        print(render_for(sys.argv[2]), end="")
    elif cmd == "open":
        print(render_open(), end="")
    elif cmd == "board":
        print(render_board(), end="")


if __name__ == "__main__":
    main()
