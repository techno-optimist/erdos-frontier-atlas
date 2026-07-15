# DGX Foundry deployment

The DGX is the only runtime tier. The Mac checkout is for code and review.

## Control law

- Research agent: the SGLang Qwen 35B endpoint at `127.0.0.1:30000`.
- Cadence: reuse the existing `chronos-frontier-scout` and night-shift jobs.
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

The scheduled agent should read the JSON written at
`~/.hermes/chronos_state/foundry_stall_gate.json`. If
`frontier_call_allowed` is true, it may run exactly one consultation:

```bash
python3 ~/erdos-frontier-atlas/tools/foundry.py consult \
  --state ~/.hermes/chronos_state/foundry_frontier_budget.json \
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

`foundry/deploy_jobs.py` performs the one-time scheduler migration under the
Hermes cron lock, writes a timestamped backup, pins both research jobs to the
local 35B provider, and appends the recursion instruction idempotently.

The checked-in `40-foundry-tool-parser.conf` preserves the live W19/MoE hooks
while enabling SGLang's `qwen3_coder` tool-call parser. Install it as the
highest-priority `chronos-sglang.service.d` drop-in, daemon-reload, restart, and
require both `/health` and an actual parsed tool call before declaring the
research agent live.
