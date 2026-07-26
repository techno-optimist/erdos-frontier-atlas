# erdos-frontier-atlas — agent context

This repo is a machine-readable annex to erdosproblems.com: 1,217 problem
records, replayable certificates, and feasibility overlays, maintained under
strict provenance discipline.

**Cold start: read [`GRAPH.md`](GRAPH.md) first** — it is the four-read
protocol (entry point → [`views/sorties.md`](views/sorties.md) strike board →
one attack card in `views/graph/` → your lane). The do-not-spend list renders
before the targets; read it in that order.

**Before writing anything: read [`COORDINATION.md`](COORDINATION.md) and
register your lane.** Its rules bind every session — work on your own branch
and reach `main` by PR only, never push to `main`; merged
`certificates/<slug>/` are FROZEN (extend with new files, never regenerate);
commit every proof object; never clobber another agent's files. The charter
([`FRONTIER_CARTOGRAPHY.md`](FRONTIER_CARTOGRAPHY.md) §2 tenets, §6 honest
scope, §8 agent protocol) binds every action.

Standing rules (1, 3, 4, 5 are gated by `make check-graph` + `make test`;
2 holds by builder construction — the ranking predicate never reads `prize`):

1. **A claim never sets a status.** Statuses come from `atlas/stubs.json` and
   replayable evidence only.
2. **Prizes are history, not targets.** Six prize-bearing "falsifiable"
   problems are documented traps (`views/sorties.md`, first table).
3. **Walls are per-branch.** #64 is a $1000 trap on its general branch and a
   vetted target on its cubic branch — read the card, not just the status.
4. **Never hand-edit generated files** (`atlas/graph/`, `views/sorties.md`,
   `views/graph/`, `views/state_of_frontier.md`, `views/index.md`,
   `book/BOOK.md`) — fix the source ledger and rerun `make graph` /
   `make state-of-frontier` / `python3 tools/build_stubs.py` / `make book`.
5. **No erdosproblems.com prose** — link-only problems stay link-only
   (licensing firewall).

Before merging anything under `certificates/`: `make check-receipts`.
Full gate: `make audit-fast`.
