# Releasing EFA-DR1 (and every DR-n after it)

The gap map ships as **numbered data releases** (DR1, DR2, …), sky-survey style,
each with its own DOI (charter [WS1](FRONTIER_CARTOGRAPHY.md)). This file is the
release procedure. It has two kinds of steps: a machine-checkable gate any agent
or the lead can run, and **two steps that are human-only by policy** — no agent
performs them, ever (charter WS10: external submissions are always human-sent).

## 1. The machine gate (run before anything else)

All of these must pass on the release candidate, in this order:

```sh
python3 tools/validate_gap_map.py     # structure + WS7 epistemic ledger: every entry's
                                      # confidence class recomputed from its evidence[]
python3 tools/validate_atlas.py       # release-count locks on the 51-problem tier
                                      # (needs: python3 -m pip install -r requirements-dev.lock)
python3 -m pytest tests/ -q           # contract tests
make check-views                      # views/state_of_frontier.md not stale vs the data
make verify-certs                     # replay the fast in-repo certificate verifiers
time make hello-frontier              # the stranger's quickstart, INCLUDING the DRAT
                                      # negative control — must complete well under 10
                                      # minutes (measured 2026-07-18: 3–20 s cold on a
                                      # laptop, dominated by the pinned drat-trim
                                      # clone+build; <1 s with the build cached)
```

If any check fails, there is no release candidate. Do not weaken a check to get
one (house rule; also Tenet 4 — the epistemic state is explicit or it is nothing).

## 2. HUMAN-ONLY STEP 1 — mint the Zenodo DOI

**The release gate is a live DOI: EFA-DR1 does not ship without it** (charter WS1).
`CITATION.cff` deliberately carries `doi: "TBD"` and no `date-released` until this
step happens. Only the human lead does this, because it is an external submission
under an external account.

Recommended order (reserve-first, so the archived `CITATION.cff` cites itself):

1. On Zenodo, create a new upload and use **"Reserve DOI"** to get the concrete
   DOI *before* publishing.
2. Write that DOI into `CITATION.cff` (`doi:` replaces `TBD`) and set
   `date-released:` to the actual release date. Commit.
3. Confirm the licensing decision (step 3 below) — the Zenodo deposit's license
   field must match what the repository states.
4. Tag the release commit (suggested tag: `efa-dr1`) and upload the tagged
   archive to the reserved deposition (or use Zenodo's GitHub-release
   integration pointed at the tag).
5. Fill the Zenodo metadata from `CITATION.cff` (title, author, version `DR1`,
   keywords, abstract) and **publish**. Note: the repo's `.zenodo.json` still
   carries the *51-problem-atlas* description (its board-count facts are
   pinned by `tools/validate_atlas.py`), and the GitHub–Zenodo integration
   would use it verbatim — reconcile it with the DR1 `CITATION.cff` at mint
   time, keeping every pinned fact, or enter the deposit metadata manually.
6. Verify the DOI resolves, then update the README/board with the citable
   release row.

Subsequent releases repeat this with a new version (`DR2`, …) and a new DOI;
Zenodo's versioning links them under one concept DOI.

## 3. HUMAN-ONLY STEP 2 — confirm the data/tools licensing split

**Current state of record:** this repository has a single [`LICENSE`](LICENSE)
file — MIT, © 2026 Kevin Russell — covering everything, and `CITATION.cff` says
`license: MIT` to match. That is what is true today; nothing else has been
changed by agents, deliberately.

**The proposal** (charter WS1 names it: "licensing stated — CC-BY 4.0 for data,
MIT for tools"):

- **CC-BY-4.0** for the *data*: `atlas/*.json`, `views/`, the certificate data
  artifacts (CNF/DRAT files, witness and table JSON, certificate READMEs), and
  `progress/` receipts.
- **MIT** for the *tools*: `tools/`, `scripts/`, `tests/`, the `Makefile`, and
  the `verify.py` checkers (code stays MIT wherever it lives, including inside
  `certificates/`).

**Why this is a human decision, not an agent edit:** relicensing is a rights
decision by the copyright holder, and two upstream considerations need a human
call:

1. `atlas/stubs.json` is compiled from two **Apache-2.0** sources
   ([`teorth/erdosproblems`](https://github.com/teorth/erdosproblems),
   [`google-deepmind/formal-conjectures`](https://github.com/google-deepmind/formal-conjectures))
   with attribution in [`NOTICE`](NOTICE). Confirm that distributing that
   compiled data under CC-BY-4.0 preserves the Apache-2.0 attribution
   obligations (the `NOTICE` file must ship with the data either way).
2. Gap-map entries cite OEIS sequences. The entries record *facts and
   citations*, not OEIS prose, but OEIS content itself is CC-BY-NC — the lead
   should confirm this posture before stamping a commercial-use-permitting
   license on the dataset.

**If confirmed**, the implementation is: add the CC-BY-4.0 text as a second
license file scoped to the data paths, state the split in the README, flip the
`license:` field in `CITATION.cff` for the dataset, and set the same license on
the Zenodo deposit. **If declined**, everything simply stays MIT and only the
Zenodo license field needs to say so. Either outcome must be recorded before
step 2.5 (the Zenodo license field) is filled.

## 4. After the release

- Bump `version:` in `CITATION.cff` to the next `DR-n` (with `doi:` back to
  `TBD`) on the first post-release data change.
- From DR2 onward, the "Movement changelog" section of
  [`views/state_of_frontier.md`](views/state_of_frontier.md) is generated as
  the mechanical bracket-diff against the previous release — the stub table and
  its row format are already in the DR1 report.
- Cadence per the charter: the State of the Frontier report ships quarterly;
  releases are numbered, each with its own DOI.
