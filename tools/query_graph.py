#!/usr/bin/env python3
"""Query atlas/graph/graph.json from the command line (stdlib, read-only).

  python3 tools/query_graph.py plan                 # the strike list, compact
  python3 tools/query_graph.py card 64              # print the attack card
  python3 tools/query_graph.py neighbors 64         # every edge touching P64
  python3 tools/query_graph.py bridges 1            # shared-OEIS + tag family
  python3 tools/query_graph.py traps                # the priced trap table
  python3 tools/query_graph.py disagreements        # cross-register cells
  python3 tools/query_graph.py hot                  # external-claim queue

Everything here is also greppable without this tool — see GRAPH.md for the
grep grammar. This CLI is a convenience, not a dependency.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_graph():
    with open(ROOT / "atlas" / "graph" / "graph.json", encoding="utf-8") as f:
        return json.load(f)


def cmd_plan(graph, _args):
    nodes = {n["id"]: n for n in graph["nodes"]}
    tri = [n for n in graph["nodes"] if n["type"] == "surface"
           and n["overlay"] == "finite_handle_triage"]
    print("T1  triage TARGET branches:")
    for s in sorted((s for s in tri if s["verdict"] == "TARGET"),
                    key=lambda s: s["problem"]):
        print(f"  #{s['problem']:<5} {s['smallest_untested_case'][:100]}")
    movable = sorted({n["erdos_id"] for n in graph["nodes"]
                      if n["type"] == "problem"
                      and (n["status"] == "movable"
                           or (n.get("deep") or {}).get("beatable") == "MOVABLE")})
    print("T2  movable boards: " + ", ".join(f"#{i}" for i in movable))
    workable = sorted((int(e["dst"].split(":")[2])
                       for e in graph["edges"]
                       if e["type"] == "applies"
                       and e["src"] == "M:witness-local-search"
                       and e.get("predicate") == "workable"))
    print(f"T3  workable gap surfaces ({len(workable)}): "
          + ", ".join(f"#{i}" for i in workable[:30])
          + (" …" if len(workable) > 30 else ""))
    print("T4  triage MAYBE branches: "
          + ", ".join(f"#{s['problem']}" for s in
                      sorted((s for s in tri if s["verdict"] == "MAYBE"),
                             key=lambda s: s["problem"])))
    print("Full board: views/sorties.md — do-not-spend list renders first.")


def cmd_card(_graph, args):
    path = ROOT / "views" / "graph" / f"P{int(args[0])}.md"
    if not path.exists():
        print(f"no card for #{args[0]} — the problem has no recorded surface, "
              "wall, evidence, or hot claim. Registers live in "
              "atlas/stubs.json; a gap_map row is how a surface is born.")
        raise SystemExit(1)
    print(path.read_text(encoding="utf-8"))


def cmd_neighbors(graph, args):
    pid = f"P{int(args[0])}"
    if not any(n["id"] == pid for n in graph["nodes"]):
        print(f"unknown problem {pid}")
        raise SystemExit(1)
    for e in graph["edges"]:
        if pid in (e["src"], e["dst"]):
            extra = {k: v for k, v in e.items()
                     if k not in ("type", "src", "dst", "tier", "source")}
            print(f"{e['type']:14} {e['src']} -> {e['dst']} [{e['tier']}]"
                  + (f"  {json.dumps(extra, ensure_ascii=False)[:120]}"
                     if extra else ""))


def cmd_bridges(graph, args):
    pid = f"P{int(args[0])}"
    nodes = {n["id"]: n for n in graph["nodes"]}
    found = False
    for e in graph["edges"]:
        if e["type"] == "same_family" and pid in (e["src"], e["dst"]):
            other = e["dst"] if e["src"] == pid else e["src"]
            card = ROOT / "views" / "graph" / f"{other}.md"
            where = (f"card views/graph/{other}.md" if card.exists()
                     else "no card — registers in atlas/stubs.json")
            print(f"{other}  shares {', '.join(e['shared'])}  ({where})")
            found = True
    if not found:
        p = nodes.get(pid)
        if p is None:
            print(f"unknown problem {pid}")
            raise SystemExit(1)
        print("no shared-OEIS family; tag neighbors via: "
              + "  |  ".join(f"grep -rl '`{t}`' views/graph/"
                             for t in p["tags"][:2]))


def cmd_traps(graph, _args):
    for e in sorted((e for e in graph["edges"] if e["type"] == "trap"),
                    key=lambda e: int(e["src"][1:])):
        prize = e["prize"] if e["prize"] != "no" else "-"
        print(f"#{int(e['src'][1:]):<5} prize {prize:<7} upstream "
              f"{e['upstream_finite_handle']:<12} — walled; see the card's "
              "STOP section")


def cmd_disagreements(graph, _args):
    cells = sorted(n["erdos_id"] for n in graph["nodes"]
                   if n["type"] == "problem" and n["status"] == "solved-upstream"
                   and (n.get("deep") or {}).get("beatable") == "MOVABLE")
    print("solved-upstream x deep MOVABLE: "
          + ", ".join(f"#{c}" for c in cells))
    tri_targets = {n["problem"] for n in graph["nodes"]
                   if n["type"] == "surface"
                   and n.get("overlay") == "finite_handle_triage"
                   and n.get("verdict") == "TARGET"}
    traps = {int(e["src"][1:]) for e in graph["edges"] if e["type"] == "trap"}
    split = sorted(tri_targets & traps)
    print("trap x TARGET branch split:   "
          + ", ".join(f"#{c}" for c in split))
    walls = sorted(n["erdos_id"] for n in graph["nodes"]
                   if n["type"] == "problem" and n["status"] == "wall")
    print("upstream Open x our wall:     "
          + ", ".join(f"#{c}" for c in walls))


def cmd_hot(graph, _args):
    hot = sorted({n["erdos_id"] for n in graph["nodes"]
                  if n["type"] == "external_claim" and n.get("hot")})
    print(f"{len(hot)} hot external claims (a claim never sets a status): "
          + ", ".join(f"#{c}" for c in hot))


COMMANDS = {"plan": cmd_plan, "card": cmd_card, "neighbors": cmd_neighbors,
            "bridges": cmd_bridges, "traps": cmd_traps,
            "disagreements": cmd_disagreements, "hot": cmd_hot}


def main():
    # Keep the executable examples deterministic on Windows, where redirected
    # stdout otherwise defaults to a legacy code page that cannot encode the
    # Unicode punctuation used by the rendered graph.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__.strip())
        raise SystemExit(2)
    try:
        COMMANDS[sys.argv[1]](load_graph(), sys.argv[2:])
    except (IndexError, ValueError):
        print(f"{sys.argv[1]}: expected a problem id, "
              f"e.g. `python3 tools/query_graph.py {sys.argv[1]} 64`\n")
        print(__doc__.strip())
        raise SystemExit(2)


if __name__ == "__main__":
    main()
