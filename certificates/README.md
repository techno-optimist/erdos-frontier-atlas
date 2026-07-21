# Certificates — conventions

Each subdirectory is one result: exact, replayable, and checkable by a stranger who trusts nothing
here. The point is not that we ran something; it is that **you** can.

## The replay contract

Every certificate advertises a one-liner. It must actually work, from the certificate's own directory:

```bash
python3 -I <script>.py
```

`-I` (isolated mode) is deliberate — it keeps the replay hermetic against the reader's installed
packages, so a green result is about the certificate and not about their machine.

**The trap:** `-I` implies `-P`, which removes the script's own directory from `sys.path`. Any script
importing a *sibling* module therefore dies with `ModuleNotFoundError` under the very command we
publish. Scripts that import a sibling must re-add their directory first:

```python
import sys as _sys, pathlib as _pathlib
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import my_sibling_module          # now resolves under -I
```

This is enforced by `tests/test_certificate_replay.py`. It is a test rather than a guideline because
it bit us twice in one day, and both times the symptom was that **our own published instructions
produced a traceback**. A reader who cannot run the command cannot check the claim.

## The rest of the house style

- **Exact arithmetic.** `Fraction`/integers, stdlib-preferred. A float in the trust path is a bug.
- **Planted-failure controls.** Every certificate ships mutations that MUST fail. A checker that
  cannot fail is not a checker — we shipped a vacuously-passable detector once and an adversary,
  not the test suite, is what caught it.
- **Never overwrite your own artifact on replay.** A verifier that rewrites its committed JSON makes
  every replay dirty the working tree, which hides real drift and blocks branch switches. Check the
  artifact; do not regenerate it. Timing fields especially do not belong in committed output.
- **State the boundary in the header, not in a review.** What is *not* certified goes where a reader
  hits it first. If prose claims more than the machine checks, the prose is the bug — that is the
  single most common defect in this repo's history, by a wide margin.
- **Claim-typing.** Say plainly which parts are ours, which are external, and what remains
  conditional. Search-bounded negatives are fences, not proofs, and must be labelled as such.
