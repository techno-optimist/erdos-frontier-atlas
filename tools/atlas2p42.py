#!/usr/bin/env python3
"""atlas2p42 — compile an Erdos Frontier Atlas entry into a P42 problem skeleton.

Usage:
    python3 tools/atlas2p42.py --id 21 --slug q6-intersecting-hypergraph \
        --out /path/to/p42-prizes/problems [--verifier my_verify_stub.py] \
        [--direction minimize --score-name edge_count --seed-best 18/1]

Reads atlas/problems.json, selects the entry (by --id or --slug; a stored
p42_slug wins if --slug is omitted), and writes a problems/<slug>/ skeleton
matching the structure of the five real Phase-A packages
(q6-intersecting-hypergraph et al. in p42-prizes):

    <slug>/
      problem.yaml            p42-problem/v1 metadata (objective, verifier, settlement, DA)
      SPEC.md                 problem statement + solution format + verifier contract (template)
      solution.schema.json    JSON Schema draft 2020-12 with x-p42-max-bytes (template)
      Makefile                verify / verify-seed / verify-open-witness / lint / test targets
      BOUNTY.md               Phase-0 settlement metadata
      HARDENING.md            R1-R4 checklist template (exact arithmetic, recompute-never-echo,
                              determinism, total+bounded)
      LEADERBOARD.md          local reference rows
      Dockerfile              python:3.14-slim runner
      requirements.lock       stdlib-only marker
      verifier/verify.py      stub (or a copy of --verifier)
      tests/                  fixture dir seeded with lying-claim.json + malformed.json stubs
                              and a pytest scaffold
      examples/               empty dir for reference witnesses

Everything generated is a SKELETON: TODO markers must be resolved and the
package must pass `p42-prizes lint / validate / verify` with real fixtures
before admission. The compiler is mechanical on purpose — the schemas align
1:1 (finite_object -> solution.schema.json; exact verifier -> verifier/verify.py
-> VerdictReport; current record -> open-witness seed; min_improvement gate).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ATLAS = Path(__file__).resolve().parents[1] / "atlas" / "problems.json"


def die(msg: str) -> None:
    print(f"atlas2p42: error: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_entry(args: argparse.Namespace) -> dict:
    doc = json.loads(ATLAS.read_text(encoding="utf-8"))
    problems = doc["problems"]
    if args.id is not None:
        hits = [p for p in problems if p["id"] == args.id]
    elif args.slug:
        hits = [p for p in problems if p.get("p42_slug") == args.slug]
    else:
        die("need --id or --slug")
    if not hits:
        die("no atlas entry matched")
    return hits[0]


def problem_yaml(slug: str, entry: dict, a: argparse.Namespace) -> str:
    return f"""schema_version: p42-problem/v1
problem_id: {slug}
title: Erdos {entry['id']} / {entry['title']}
status: phase-0-packaging
objective:
  direction: {a.direction}
  score_name: {a.score_name}
  seed_best: "{a.seed_best}"  # TODO: pin to the verified current record with source
  optimum: null  # TODO: proven bound if one exists (metadata only, never a verifier check)
  min_improvement: "{a.min_improvement}"
  gauge: "max(0, seed_best - score)"  # TODO: adjust for direction
verifier:
  version: "0.1.0"
  image: "sha256:local-dev"
  command: "python3 verifier/verify.py --solution {{solution}}"
  max_compute:
    wall_seconds: 5      # TODO: measure worst-case end-to-end and leave >= 10x headroom
    memory_mb: 128
settlement:
  chain: base-sepolia
  pool_address: null
  challenge_window_seconds: 259200
  posting_bond_wei: "0"
  challenge_bond_wei: "0"
data_availability:
  commit_time_blob: local-file-for-phase-0
  finalize_receipt: optional-mirror  # DA rides reveal calldata (sha256==commitDaHash); Arweave permanence is an optional mirror, not required (see docs/DATA_AVAILABILITY.md)
"""


def spec_md(slug: str, entry: dict) -> str:
    links = entry.get("links", {})
    oeis = " ".join(links.get("oeis", [])) or "(none)"
    arxiv = " ".join(f"arXiv:{x}" for x in links.get("arxiv", [])) or "(none)"
    return f"""# {entry['title']}

Erdos problem #{entry['id']} — {entry['erdos_url']}

## Problem

{entry['statement']}

**Finite object.** {entry['finite_object']}

## Known frontier (verify against primary sources before admission)

{entry.get('frontier') or 'TODO'}

Full record notes: see the atlas entry (`atlas/problems.json`, id {entry['id']}).
References: OEIS {oeis} · {arxiv}

## Solution format

TODO: canonical JSON, mirrored exactly by `solution.schema.json`
(including `x-p42-max-bytes`). Document every field, every bound, and why
each bound is LOSSLESS (no genuine witness excluded).

## What the verifier checks (all exact integer/rational arithmetic)

TODO, derived from the atlas verifier spec:

> {entry['verifier']}

1. **Shape**: schema-level bounds re-checked in code.
2. **Structure**: the defining combinatorial conditions, full coverage, no sampling.
3. **Score**: recomputed from the witness alone (recompute-never-echo);
   submitter claim fields are ignored.

Include a completeness argument (lemma + proof) for any search the verifier
performs, and a node/operation bound showing the check is total and bounded
a priori.

## Score and improvement

```text
score = TODO (exact rational "num/den")
improvement = max(0, seed_best - score)   # TODO: adjust for direction
minImprovement = TODO
```

A witness is `valid` iff it passes every structural check AND
`improvement >= minImprovement`. A structurally sound but non-improving
witness reports its true recomputed score with reason `NOT_STRICT_IMPROVEMENT`.

## References

TODO: primary sources for every number quoted above.
"""


def solution_schema(slug: str) -> str:
    return json.dumps(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"https://p42.xyz/problems/{slug}/solution.schema.json",
            "x-p42-max-bytes": 65536,
            "type": "object",
            "required": ["TODO_witness_field"],
            "additionalProperties": False,
            "properties": {
                "source": {"type": "string"},
                "claimed_improvement": {"type": "string"},
                "claimed_score": {"type": "string"},
                "TODO_witness_field": {
                    "description": "TODO: mirror the finite object exactly; every bound lossless",
                    "type": "array",
                    "items": {"type": "integer"},
                },
            },
        },
        indent=2,
    ) + "\n"


def makefile(slug: str) -> str:
    return """PYTHON ?= python3
SOLUTION ?= tests/lying-claim.json
PYTHONPATH := ../../src

.PHONY: verify verify-seed verify-open-witness lint test

verify:
\t@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m p42_prizes.cli verify --problem . --solution $(SOLUTION)

verify-seed:
\t@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m p42_prizes.cli seed-check --problem . --solution $(SOLUTION)

verify-open-witness:
\t@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m p42_prizes.cli seed-check --problem . --solution $(SOLUTION) --require-strict

lint:
\t@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m p42_prizes.cli lint --problem .

test:
\t@PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest -q tests
"""


def bounty_md(entry: dict) -> str:
    return f"""# Bounty Metadata

Status: Phase 0 packaging only. No real ETH, no audited contracts, no legal
review, and no immutable verifier image.

- Chain: Base Sepolia
- Pool address: not deployed
- Challenge window: 259200 seconds
- Posting bond: 0 wei for local packaging
- Challenge bond: 0 wei for local packaging
- Commit preimage: `keccak(answerCID || solverAddr || salt)`
- Data availability: local file for Phase 0; on-chain-at-reveal calldata
  (`sha256(bytes) == commitDaHash`) once funded.
- Min improvement: TODO.

Naming note: this is an independent computational frontier bounty on Erdos
problem #{entry['id']}, administered by P42 Prizes. It is NOT Erdos's own
historical prize, which is administered separately and (for this problem)
attaches to an asymptotic statement no finite computation can claim.
"""


def hardening_md() -> str:
    return """# Hardening Notes (template — every section must be made TRUE before admission)

## R1 - Exact arithmetic

TODO: only Python integers / `fractions.Fraction`; no float literals, no true
division, no `math.*`, no float-prone imports; `p42_prizes.cli lint` passes.

## R2 - Recompute, never echo

TODO: the verifier reads only the witness fields. Ship a `tests/lying-claim.json`
fixture whose claimed score is better than its true score and assert the
verifier reports the TRUE recomputed score.

## R3 - Determinism and reproducibility

TODO: pure stdlib; no random/clock/network/locale/env/filesystem reads beyond
the solution path; canonical JSON output (sorted keys, exact "num/den"
rationals) via the shared VerdictReport writer; identical bytes in =>
identical report out.

## R4 - Total and bounded

TODO: input bytes capped (x-p42-max-bytes) before parsing via
`read_bounded_solution`; every malformed input returns a typed failure report;
catch-all INTERNAL report; a-priori work bound stated and measured; declared
`wall_seconds` >= 10x measured worst case.
"""


def leaderboard_md() -> str:
    return """# Leaderboard

This package has no on-chain submissions. Local reference row:

| solution | score | improvement | notes |
|---|---:|---:|---|
| TODO seed fixture | TODO | `0/1` | TODO: the seed witness IS the current record and earns no improvement. |
"""


def dockerfile() -> str:
    return """FROM python:3.14-slim

WORKDIR /problem
COPY . /problem
COPY ../../src /src
ENV PYTHONPATH=/src

ENTRYPOINT ["python", "verifier/verify.py"]
"""


def verifier_stub(slug: str, entry: dict) -> str:
    return f'''#!/usr/bin/env python3
"""Verifier stub for {slug} (Erdos #{entry["id"]}).

Contract (see HARDENING.md): exact integer/rational arithmetic only;
recompute-never-echo; deterministic; total and bounded on byte-capped input;
emit a canonical VerdictReport.

Atlas verifier spec:
{entry["verifier"]}
"""
from __future__ import annotations

import argparse

# TODO: from p42_prizes.verdict import VerdictReport, read_bounded_solution


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", required=True)
    args = parser.parse_args()
    raise NotImplementedError(
        "TODO: implement the exact checks from SPEC.md; "
        "never read claimed_* fields; emit a canonical VerdictReport"
    )


if __name__ == "__main__":
    main()
'''


def test_scaffold(slug: str) -> str:
    mod = slug.replace("-", "_")
    return f'''from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

import jsonschema


PROBLEM = Path(__file__).resolve().parents[1]
ROOT = PROBLEM.parents[1]
VERDICT_SCHEMA = json.loads(
    (ROOT / "schemas" / "verdict.schema.json").read_text(encoding="utf-8")
)


def run_verify(solution: str | Path) -> tuple[int, dict]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    completed = subprocess.run(
        ["make", "verify", f"SOLUTION={{solution}}"],
        cwd=PROBLEM,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.stdout, completed.stderr
    report = json.loads(completed.stdout)
    jsonschema.validate(report, VERDICT_SCHEMA)
    return completed.returncode, report


def test_lying_claim_recomputed() -> None:
    # TODO({mod}): fixture must claim a better score than it earns;
    # assert the verifier reports the TRUE recomputed score.
    _, report = run_verify(PROBLEM / "tests" / "lying-claim.json")
    raise NotImplementedError("TODO: assert recomputed score, not the claim")


def test_malformed_is_typed_failure() -> None:
    code, report = run_verify(PROBLEM / "tests" / "malformed.json")
    raise NotImplementedError("TODO: assert typed failure reason")
'''


def build(entry: dict, slug: str, out_root: Path, a: argparse.Namespace) -> Path:
    dest = out_root / slug
    if dest.exists() and not a.force:
        die(f"{dest} exists (use --force to overwrite)")
    (dest / "tests").mkdir(parents=True, exist_ok=True)
    (dest / "verifier").mkdir(exist_ok=True)
    (dest / "examples").mkdir(exist_ok=True)

    (dest / "problem.yaml").write_text(problem_yaml(slug, entry, a), encoding="utf-8")
    (dest / "SPEC.md").write_text(spec_md(slug, entry), encoding="utf-8")
    (dest / "solution.schema.json").write_text(solution_schema(slug), encoding="utf-8")
    (dest / "Makefile").write_text(makefile(slug), encoding="utf-8")
    (dest / "BOUNTY.md").write_text(bounty_md(entry), encoding="utf-8")
    (dest / "HARDENING.md").write_text(hardening_md(), encoding="utf-8")
    (dest / "LEADERBOARD.md").write_text(leaderboard_md(), encoding="utf-8")
    (dest / "Dockerfile").write_text(dockerfile(), encoding="utf-8")
    (dest / "requirements.lock").write_text(
        "# stdlib-only verifier path; pytest is used by the repository test harness.\n",
        encoding="utf-8",
    )
    if a.verifier:
        shutil.copyfile(a.verifier, dest / "verifier" / "verify.py")
    else:
        (dest / "verifier" / "verify.py").write_text(
            verifier_stub(slug, entry), encoding="utf-8"
        )
    mod = slug.replace("-", "_")
    (dest / "tests" / f"test_{mod}.py").write_text(test_scaffold(slug), encoding="utf-8")
    (dest / "tests" / "lying-claim.json").write_text(
        '{\n  "TODO": "structurally sound witness whose claimed_score beats its true score"\n}\n',
        encoding="utf-8",
    )
    (dest / "tests" / "malformed.json").write_text("{not json\n", encoding="utf-8")
    return dest


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--id", type=int, help="erdosproblems.com id in the atlas")
    p.add_argument("--slug", help="board slug (defaults to the entry's p42_slug)")
    p.add_argument("--out", required=True, help="p42-prizes problems/ directory")
    p.add_argument("--verifier", help="path to a real verifier to copy instead of the stub")
    p.add_argument("--direction", default="minimize", choices=["minimize", "maximize"])
    p.add_argument("--score-name", default="score")
    p.add_argument("--seed-best", default="TODO/1")
    p.add_argument("--min-improvement", default="1/1")
    p.add_argument("--force", action="store_true")
    a = p.parse_args()

    entry = load_entry(a)
    if entry.get("board_class") == "NONE":
        die(
            f"atlas entry #{entry['id']} is board_class NONE ({entry.get('wall_reason')}) - "
            "walls do not get boards"
        )
    slug = a.slug or entry.get("p42_slug")
    if not slug:
        die("entry has no p42_slug; pass --slug")
    dest = build(entry, slug, Path(a.out), a)
    print(f"wrote skeleton: {dest}")
    print("next: resolve every TODO, add real fixtures, then run make lint && make test")


if __name__ == "__main__":
    main()
