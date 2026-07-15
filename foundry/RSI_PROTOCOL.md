# Foundry recursive-improvement protocol

## Current epistemic status

Foundry is currently **Level 0: delegated autonomous search**. It continuously
selects mathematical frontiers, runs local-Qwen-35B experiments, verifies what
it can, and publishes typed provisional receipts. That is useful autonomy, but
it is not yet evidence of recursive self-improvement.

The Level 1 claim becomes testable only when a harness-authored mutation beats
the frozen harness on independently adjudicated held-out mathematics under the
same model, token, API-call, wall-clock, and frontier-call budgets. Level 2
requires the accepted improved harness to become a measurably better harness
improver in the next generation. Token compression, self-editing, uninterrupted
runtime, or higher receipt volume do not establish either claim.

The machine-readable contract is [`rsi_protocol.json`](rsi_protocol.json).

## Hypothesis and falsifier

**Question.** Do Foundry-authored harness mutations increase independently
verified mathematical utility across heterogeneous held-out task families,
without semantic drift or reward hacking?

**Hypothesis.** Role-specific compact context, verifier-first branching, and
evidence-yield-aware exploration improve held-out verified utility at a fixed
local-Qwen-35B budget.

**Falsifier.** Reject the mutation if its paired held-out utility does not
improve, the improvement vanishes under equal budgets, any hard safety gate
regresses, or the gain is restricted to visible development problems.

## Frozen experiment

The visible development suite contains six problems across exact search,
nonexistence/certificate work, and constructive/local search. A separate
twelve-task holdout uses the same family balance and two frozen seeds per task.
Baseline and candidate therefore receive 36 paired task-runs each: 12 visible
development runs and 24 promotion-bearing holdout runs.

Each task-run is capped at:

- the same `/home/chronos/models/qwen3.6-35b-a3b` weights;
- 1,500,000 model input tokens and 100,000 output tokens;
- 24 API calls and 1,200 wall-clock seconds;
- zero frontier-model calls.

The worker reserves the final two calls inside that unchanged 24-call budget
for typed `submit_result` attempts. At the reserve boundary it stops exploration
and forces the submission tool, so a bounded negative or blocked result is
still emitted when no improvement was found. A missing or malformed result
remains a failed run; the evaluator does not synthesize mathematical evidence
on the candidate's behalf.

The no-frontier-call rule isolates harness quality from purchased strategy.
Consultation is evaluated separately after the local-only core passes.

The holdout must be evaluator-owned and inaccessible to candidate workers by
an OS or container boundary. A `0600` file owned by the same account is not an
adequate secret because an agent with shell tools could read it. Until that
isolation gate exists, all results are development telemetry and promotion is
disabled.

`tools/foundry_eval.py` creates a salt-keyed, family-balanced private split and
publishes only its SHA-256 commitment at
`foundry/eval/private_suite.commitment.json`. Its Docker smoke boundary uses a
read-only root filesystem, no network, no capabilities, no Docker socket, and
mounts exactly one task packet plus an output directory; the private manifest
is never mounted. `model-transport-smoke` and `candidate-run` retain that
boundary while mounting one evaluator-owned Unix-domain socket. The container
has no TCP network, host address, credentials, Docker socket, or private
manifest; the host membrane forwards only `/v1/chat/completions` to loopback,
forces the frozen Qwen model, disables streaming, and enforces API/input/output
budgets. A passing transport smoke is necessary but not sufficient: candidate
artifacts still have zero utility until the independent replay adjudicator
accepts them.

## Reward boundary

The worker's `progress`, `negative_result`, and `blocked` labels are not the
reward. They are model-adjacent and therefore gameable. An independent frozen
evaluator replays content-addressed artifacts and assigns verified-utility
units:

| Units | Independently replayed event |
|---:|---|
| 8 | theorem, exact value, or strict frontier-bound improvement accepted through a canonical certificate path |
| 4 | new exact certificate or sound pruning result that closes a live route |
| 2 | reproducible verifier or executable falsifier that materially narrows the next search |
| 1 | valid typed receipt whose claimed artifact and source provenance replay |
| 0 | blocked, prose-only, duplicate, unreplayed, or merely self-labelled work |

Primary comparison is total verified utility at the fixed budget. Paired wins,
certificate replay rate, semantic violations, input tokens, and wall time are
secondary diagnostics. Efficiency never compensates for lower verified
utility.

Production semantic rejections are also counterexamples, not discarded logs.
The no-agent publisher retains a private hash-keyed rejection record; when that
frontier is next selected, the worker receives the exact contract errors and
must replay the bounded evidence before issuing a narrower corrected receipt.
No model-authored redaction crosses the public membrane automatically.

## Promotion rule

A candidate remains in an isolated worktree. It cannot edit production jobs,
the automation branch, Atlas databases, evaluator state, or holdout manifests.
Promotion requires all of the following:

1. all unit, adversarial, public-membrane, and protected-hash gates pass;
2. at least 16 wins across 24 paired holdout runs;
3. the 95% bootstrap lower bound on mean utility delta is above zero;
4. no public-suite or hard-constraint regression;
5. independent artifact replay;
6. a human-reviewed pull request.

Automatic production promotion is deliberately disabled. Three successive
accepted generations plus a fair human-baseline comparison are the minimum for
Level 1 evidence; they are not assumed in advance.

## Resource telemetry

`tools/foundry_efficiency.py` extracts first-turn API calls, tokens, latency,
wall time, and nearest receipt metadata from Hermes logs. It stops at the first
`Turn ended` marker because Hermes background skill review reuses the same
session ID. The tool explicitly emits `utility_score: null`: only the frozen
independent evaluator may turn artifacts into utility.

Example on DGX:

```bash
python3 ~/erdos-frontier-atlas/tools/foundry_efficiency.py \
  ~/.hermes/logs/agent.log \
  --since 2026-07-15T00:00:00Z \
  --output ~/.hermes/chronos_state/foundry_efficiency_latest.json
```

This instrumentation can prove that compact context reduced compute while
preserving independently judged output. It cannot prove the preservation by
itself.

## Independent replay implementation

[`tools/foundry_adjudicate.py`](../tools/foundry_adjudicate.py) implements the
previously specified independent-replay boundary. It is run from a clean,
evaluator-owned revision, never from the candidate worktree. A positive replay
unit requires a v2 result bound to the exact task ID, seed, and canonical task
packet hash; an evaluator-computed content address for every bounded regular
artifact; a fixed-budget model-run receipt; and fresh zero-exit replay in a
second Docker container with no network, model socket, candidate workspace,
private manifest, or Docker socket.

Candidate-authored executable replay earns **zero utility units** by itself. It
establishes reproducibility, not mathematical truth. Every positive rubric
level, including the one-unit typed-receipt level, requires an evaluator-owned
canonical verdict bound to the task-packet and candidate-result hashes. The
verdict records the immutable verifier identity/source digest and is unavailable
inside both candidate and replay containers. This prevents a candidate from
promoting its own checker into a correctness oracle.

The initial canonical registry covers four exact public witness classes:
distinct subset sums (#1), q(6) (#21), van der Waerden lower-bound colorings
(#138), and C4-versus-star Ramsey witnesses (#552). It accepts only a strict
improvement over the frozen frontier; reproductions and known witnesses score
zero. Other task classes remain honestly unscored until an evaluator-owned
verifier is registered. In particular, replay infrastructure being operational
does not by itself open the Level 1 promotion gate.

The same tool performs paired comparison. It refuses incomplete matrices,
different task-packet hashes, or different fixed model/budget evidence. Every
baseline and candidate output must also have completed fresh artifact replay;
a pair with a missing or failed replay is telemetry, not operational paired
evidence and cannot promote. The comparator applies the frozen holdout win and
bootstrap gates and always leaves automatic production promotion disabled. Its
`smoke` command is explicitly labelled synthetic boundary evidence and cannot
count as RSI evidence. The complete machine-readable membrane is frozen in
[`adjudication_protocol.json`](adjudication_protocol.json).
