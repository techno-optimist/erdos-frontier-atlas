# erdos-frontier-atlas — agent context

This repo is a machine-readable annex to erdosproblems.com: 1,217 problem
records, replayable certificates, and feasibility overlays, maintained under
strict provenance discipline.

**Cold start: read [`GRAPH.md`](GRAPH.md) first** — it is the four-read
protocol (entry point → [`views/sorties.md`](views/sorties.md) strike board →
one attack card in `views/graph/` → your lane). The do-not-spend list renders
before the targets; read it in that order.

Standing rules (mechanically enforced — `make check-graph`, `make test`):

1. **A claim never sets a status.** Statuses come from `atlas/stubs.json` and
   replayable evidence only.
2. **Prizes are history, not targets.** Six prize-bearing "falsifiable"
   problems are documented traps (`views/sorties.md`, first table).
3. **Walls are per-branch.** #64 is a $1000 trap on its general branch and a
   vetted target on its cubic branch — read the card, not just the status.
4. **Never hand-edit generated files** (`atlas/graph/`, `views/sorties.md`,
   `views/graph/`, `views/state_of_frontier.md`, `book/BOOK.md`) — fix the
   source ledger and rerun `make graph` / `make state-of-frontier` /
   `make book`.
5. **No erdosproblems.com prose** — link-only problems stay link-only
   (licensing firewall).

Before merging anything under `certificates/`: `make check-receipts`.
Full gate: `make audit-fast`.
