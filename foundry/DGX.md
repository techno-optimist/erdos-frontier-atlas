# DGX Foundry deployment

The DGX is the only runtime tier. The Mac checkout is for code and review.

## Control law

- Research agent: the SGLang Qwen 35B endpoint at `127.0.0.1:30000`.
- Cadence: the optimized local-35B `chronos-frontier-scout` runs every 30
  minutes; the night shift remains the deeper daily pass.
- Truth surfaces: production Atlas databases are opened read-only by the
  existing context builder.
- Public state: `tools/foundry_tick.py` ingests labelled final receipts and
  pushes only `progress/` to `automation/frontier-scout`.
- Escape hatch: after two consecutive semantically repeated blocked/negative
  receipts, `tools/foundry.py consult` may call the honesty router's explicit
  `aperture-frontier` alias. Budget: two calls per UTC day, six-hour cooldown.
- Canonical mutation: never automatic. A receipt remains `provisional` until
  promoted through the Atlas/certificate verifier path.

## Scout instruction addition

The scheduled agent uses only `foundry.gate` in its prep output for escalation
authorization. Gate v2 filters receipts by the exact structured `frontier_id`;
a stall in one lane cannot authorize a call in another. The publisher's
`foundry_stall_gate.json` is a read-only per-lane monitoring summary, not an
authorization token. If `frontier_call_allowed` is true, the worker may run
exactly one consultation:

```bash
python3 ~/erdos-frontier-atlas/tools/foundry.py consult \
  --state ~/.hermes/chronos_state/foundry_frontier_budget.json \
  --frontier-id '<foundry.gate.frontier_id>' \
  "<public-safe frontier, failed routes, falsifier, and desired executable test>"
```

The returned text is strategy advice, not evidence. The 35B must still execute
and verify the proposed test locally. If the gate is closed or consultation
fails, it records a blocked/negative receipt and rotates.

## Publisher smoke

```bash
python3 ~/erdos-frontier-atlas/tools/foundry_tick.py \
  --repo ~/erdos-frontier-atlas --no-push
python3 ~/erdos-frontier-atlas/tools/foundry.py validate
```

After the smoke passes, schedule the tick as a no-agent job. Git credentials
must be scoped to this public repository; the publisher refuses to stage any
path outside `progress/`.

The terminal completion gate is executable:

```bash
python3 ~/erdos-frontier-atlas/tools/foundry_audit.py \
  --output ~/.hermes/chronos_state/foundry_operational_audit.json
```

It exits nonzero until every service, live scheduler ticker, publication,
private stall-budget, advice-execution, validation, and protected-hash check is green. Use
`--allow-incomplete` only for monitoring while the final trace is pending.

Frontier advice is stored only in the private `foundry_frontier_budget.json`
state (mode `0600`) and replayed to later scheduled workers until a typed
receipt proves that its smallest test was executed. Publication contains only
the advice digest and public-safe outcome, never the private strategy text.

Before each context build, `foundry/select_frontier.py` applies an auditable
recency penalty and a smaller closed-lane penalty to the queue. Equal-priority
closed lanes therefore rotate instead of repeatedly consuming scout cycles,
while a lane with verified progress remains eligible for continued work.

DGX cron renders wall-clock timestamps in fixed MST (`UTC-07:00`), so
`foundry/config.json` uses `Etc/GMT+7`. Receipt construction cross-checks that
offset against the raw run file's absolute mtime and fails over to the latter
when they differ by more than 30 minutes. A one-time provenance repair can be
previewed, then applied, with `tools/repair_receipts.py`; it verifies every raw
source hash and emits a public old-to-new receipt-ID migration manifest.

`foundry/deploy_jobs.py` performs the one-time scheduler migration under the
Hermes cron lock, writes a timestamped backup, pins both research jobs to the
local 35B provider, points auxiliary compression at the same local provider,
replaces eager 100KB umbrella-skill injection with the compact `foundry` skill,
and appends the recursion instruction idempotently. Install `foundry/SKILL.md`
under `~/.hermes/skills/foundry/` before running the migration; specialist
skills remain available for adaptive loading after target selection.

The checked-in `40-foundry-tool-parser.conf` preserves the live W19/MoE hooks
while enabling SGLang's `qwen3_coder` tool-call parser. Install it as the
highest-priority `chronos-sglang.service.d` drop-in, daemon-reload, restart, and
require both `/health` and an actual parsed tool call before declaring the
research agent live.
