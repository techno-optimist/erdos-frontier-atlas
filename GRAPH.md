# GRAPH.md — the attack graph, in one read

You are an agent with a context window and (maybe) some compute. This repo
contains a machine-built graph over all 1,217 Erdős problems whose only job is
to answer: **where do I strike, what exactly do I run, what must my receipt
contain to be promotable, and what must I NOT touch?**

## Cold start — four reads (~42 KB)

0. **[`COORDINATION.md`](COORDINATION.md) if you are going to write anything**
   — register your lane first. Its rules bind every session: work on your own
   branch and reach `main` by PR only; merged `certificates/<slug>/` are
   FROZEN (extend with new files, never regenerate); never edit another
   agent's files. The charter ([`FRONTIER_CARTOGRAPHY.md`](FRONTIER_CARTOGRAPHY.md)
   §2 tenets, §6 honest scope, §8 agent protocol) binds every action.
1. **This file** — the protocol (you are here).
2. **`views/sorties.md`** — the Quartermaster's board: the do-not-spend list
   renders *first*, then the ranked strike list (T1 vetted targets → T4
   maybes), disagreement cells, the hot-claim queue, and one-command replay
   recipes.
3. **One attack card** — `views/graph/P<id>.md` for the problem you picked.
   Every card opens with STOP (walls, traps, retraction pins), then the
   three-register status, then branch-level attack surfaces with the exact
   witness/verifier/frontier, then what a promotable win looks like.
4. **The lane you'll use** — `atlas/lanes.md` for the move's mechanics.

Fastest first hour: run a working replay from the recipes section of
`views/sorties.md`, read its `verify.py`, then adapt the pattern to your
surface.

## Standing rules (the graph enforces these; so must you)

1. **A claim never sets a status.** Statuses come from `atlas/stubs.json` and
   evidence only. External AI claims are verification *targets*.
2. **Prizes are history, not targets.** Six of the seven prize-bearing
   "falsifiable" problems are documented traps — the prize renders beside the
   trap warning, never as a ranking key.
3. **Walls render before temptation, and walls are per-branch.** #64's general
   branch is a $1000 trap; its cubic branch is a vetted T1 target. Read the
   card, not just the status.
4. **Only cited-implication edges feed propagation.** LLM- or
   embedding-suggested edges live in `atlas/graph/quarantine.json` with zero
   weight until promoted with a source quote.
5. **Link-only problems carry no statement text** (licensing firewall — no
   erdosproblems.com prose in this repo).

## The graph itself

- `atlas/graph/graph.json` — nodes (problems, branch-level surfaces, moves,
  walls, evidence, external claims, incidents, OEIS/tag/MSC bridges, the
  jc-crater cited-implication island) and tiered edges, each carrying the
  source it was derived from. Verbatim predicates for every mechanical rule
  live under `predicates`. Everything under `jc:` is **conditional on an
  external counterexample still awaiting confirmation** — each such node
  carries that caveat in its `conditionality` field, and its
  `lit_verification` records a literature match, not a truth verdict.
- `atlas/graph/quarantine.json` — suggestion-tier material; empty in v1: the
  committed graph is 100% deterministic.
- Regenerate: `make graph` · staleness gate: `make check-graph` · rules:
  `python3 tools/validate_graph.py`. **Never hand-edit generated files** — a
  disagreement with the graph is a bug report against its sources.

## Query grammar

With the CLI (stdlib, read-only):

```
python3 tools/query_graph.py plan             # strike list, compact
python3 tools/query_graph.py card 366         # print an attack card
python3 tools/query_graph.py neighbors 64     # every edge touching P64
python3 tools/query_graph.py bridges 139      # shared-OEIS family
python3 tools/query_graph.py traps            # the priced trap table
python3 tools/query_graph.py disagreements    # cross-register cells
python3 tools/query_graph.py hot              # external-claim queue
```

Without it (grep is enough):

```
grep -n '"type": "trap"' atlas/graph/graph.json
grep -rl 'TARGET' views/graph/ | head
grep -n 'A003002' atlas/graph/graph.json      # who shares this sequence
```

## When you finish — close the loop

A result that names no graph node is a result the next agent cannot find.
Your receipt must cite the problem node (`P366`) and surface id
(`S:triage:366`) it moves; the promotion path is on every card's PROMOTE
section (gap_map `evidence[]` item → `certificates/contracts.json` claim with
sha256-pinned artifacts). Failed attacks are wall data: record what you ran
and at what scale, so the next build prices the branch honestly.
