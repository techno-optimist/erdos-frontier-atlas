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

`foundry/focused_retrieval.py` supplements the broad context builder with
read-only IDF- and phrase-ranked matches from Atlas, Atlas2, Arena, and aiwiki.
The public 51-problem frontier Atlas is a separate first-class hashed surface,
so exact problem/verifier records outrank merely thematic database matches.
Its current record and campaign finding travel with each hit, preventing a
fresh agent from repeating a solver route already falsified by prior runs.
It records before/after database hashes and writes only compact session-local
`focused_context` artifacts; failure of any read-only hash check fails prep.

Prep also binds the latest public receipt to the private accepted-source hash
and exposes it as `foundry.accepted_continuation`. Its completed action cannot
be repeated by stale queue text; the worker continues from the receipt's next
gate. This is progression state, not theorem or promotion authority.

Every prep packet also carries a hash-bound `foundry.milestone_contract`.
An untouched lane receives a verifier-and-fixtures-only milestone; an admitted
continuation receives the smallest independently replayable primitive inferred
from its next gate. The worker must copy the contract's typed Action prefix,
and the publisher rejects a missing or mismatched prefix. Implementation stops
at call 12, call 13 is final replay, and the six-field assistant response is
due by call 14. The exact-source scheduler removes every tool schema after call
13 and injects a finalization steer; the exact-source conversation loop spends
the remaining reserved calls only when the response still lacks required
labels. Writing a receipt file cannot substitute for that response. Initial
verifier milestones also reject evidence
of random/generated candidate trials; those are search, not fixtures. For the
same initial milestone, prep replaces the broad Markdown packet with a compact
hash receipt while retaining the canonical JSON for provenance and audit. This
prevents paying for focused plus broad context before a recorded need exists.

`foundry/shadow_policy.py` is an observe-only recursive-improvement layer. It
scores lane evidence yield, exploration need, age, and repeated blocking, then
writes `shadow_policy.json` into the session. It has no production selection
authority; promotion requires accumulated, auditable outcome evidence.

`foundry/RSI_PROTOCOL.md` freezes the outer-loop hypothesis, falsifier, equal
compute budget, public/private split, independent utility rubric, and promotion
gate. `tools/foundry_efficiency.py` measures only the first Hermes conversation
turn per cron session so background skill review cannot inflate research cost.
It also extracts trusted terminal durations. The publisher generates this
private report before ingest and hash-time-binds every post-policy source to a
complete same-job turn. Runs above the checked-in API, context, wall-clock, or
one-expensive-terminal budget are quarantined with structured replay feedback;
the model cannot self-report around this gate.
The report also binds the telemetry parser's source SHA-256 into its contract
digest. Parser changes invalidate the publication-policy digest and replay
hash-retained quarantines, so a fixed undercount cannot leave stale evidence.
Receipt classifications remain telemetry and never become their own reward.
The existing no-agent publisher refreshes that report every 30 minutes at
`~/.hermes/chronos_state/foundry_efficiency_latest.json` with mode `0600`; the
operational audit requires it to be fresh and explicitly authority-free.
`tools/foundry_eval.py` owns the salt-keyed private-suite commitment, one-task
packetization, and Docker isolation smoke. Candidate containers receive no
private manifest, host home, Docker socket, capability, or network. This is a
prerequisite boundary, not promotion evidence. Its model-only runner mounts an
evaluator-owned Unix-domain socket into the otherwise networkless container;
the host membrane forwards only chat completions to loopback, forces the frozen
Qwen model, and owns all token/API accounting. Run `model-transport-smoke`
before a candidate batch and store its mode-0600 report in evaluator state.
The independent artifact adjudicator must still pass before held-out scores
count.

Per-frontier `semantic_contracts` in `foundry/config.json` pin the exact target
quantity. Prep exposes the contract to the researcher, and publication fails
closed if evidence addresses a related but easier quantity or repeats a known
conflation claim. Rejected raw runs are hash-quarantined in private ingest state.
The publisher also stores a bounded structured rejection record keyed by the
immutable source hash. On the next visit to that exact frontier, prep exposes
only its errors and remediation as `foundry.quarantine_feedback`, requiring the
35B to replay the evidence and narrow the claim. The membrane never rewrites or
silently salvages a rejected receipt.

The consultation gate, router call, and private-state commit are one
cross-process locked transaction. Concurrent scout/night attempts serialize;
the later attempt re-evaluates cooldown and daily budget after the first call.

`foundry/materialize_frontiers.py` converts reviewed, provenance-tagged seeds
from `foundry/frontier_seeds.json` into DGX queue items. It is dry-run by
default; `--apply` creates a timestamped byte-for-byte backup and atomically
replaces only the private queue file. It never writes an Atlas database.
The checked-in portfolio contains eight verifier-ready public Atlas frontiers
with explicit quantity contracts. Their priorities are above retired
control-plane lanes, so the 30-minute worker rotates through actual Erdős
problems while recency penalties prevent one problem from monopolizing cycles.

DGX cron renders wall-clock timestamps in fixed MST (`UTC-07:00`), so
`foundry/config.json` uses `Etc/GMT+7`. Receipt construction cross-checks that
offset against the raw run file's absolute mtime and fails over to the latter
when they differ by more than 30 minutes. A one-time provenance repair can be
previewed, then applied, with `tools/repair_receipts.py`; it verifies every raw
source hash and emits a public old-to-new receipt-ID migration manifest.

`foundry/deploy_jobs.py` atomically installs and hash-verifies both prep copies,
the publisher entrypoint, and compact skill, then performs the scheduler
migration under the Hermes cron lock. It writes a timestamped backup, pins both research jobs to the
local 35B provider, points auxiliary compression at the same local provider,
pins the Foundry jobs to 16 turns and 900 wall-clock seconds, and installs
exact-source fail-closed Hermes scheduler hooks for both limits plus a no-tools
finalization phase after call 13. An
operator-owned job may lower, never raise, the shared gateway turn cap. Other
cron and interactive jobs retain the global Hermes behavior; restart the
gateway when these hooks are first installed.
The deployment also replaces eager 100KB umbrella-skill injection with the compact `foundry` skill,
and upserts the recursion, typed frontier-trace, runtime, and milestone
instructions so an older embedded job policy cannot survive an upgrade.
It also sets Hermes `agent.api_max_retries=8`: the bounded exponential retry
window covers the observed four-minute 35B cold reload while the SGLang
watchdog replaces a wedged worker. Permanent failures still terminate and do
not cross the publication membrane. The publisher rejects failed cron
envelopes, repairs any older mistaken acceptance, reads rotated agent logs
oldest-first, and atomically preserves the last valid efficiency report if a
refresh cannot be adjudicated.
Specialist skills remain available for adaptive loading after target selection.
Hermes background review may propose skill mutations after a research turn, but
they are not promotion-authorized: the no-agent publisher atomically restores
the reviewed repository skill on every tick, and the operational audit requires
the installed and reviewed digests to match.

The checked-in `40-foundry-tool-parser.conf` preserves the live W19/MoE hooks
while enabling SGLang's `qwen3_coder` tool-call parser. Install it as the
highest-priority `chronos-sglang.service.d` drop-in, daemon-reload, restart, and
require both `/health` and an actual parsed tool call before declaring the
research agent live.
