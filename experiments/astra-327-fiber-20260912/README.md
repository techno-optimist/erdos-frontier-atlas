# P327: multiplication can create forbidden pairs

**Method substrate, not a solution scoreboard.** This bundle gives a multiplier-sensitive refinement of Liu's smooth–rough density method.[8] It contains a self-contained informal proof, an exact compiler, and an independently recomputed small certificate. No full Erdős solution, new best bound, or formalization is claimed.

## The idea

The pair `{1,4}` has `ab/(a+b)=4/5`, so it is allowed; multiplying it by 5 gives `{5,20}`, with `ab/(a+b)=4`, so it is forbidden. Equivalently, the scaled pair has reciprocals summing to the unit fraction `1/4`. Rather than treating every rough multiplier alike, retain a finite gcd signature of it. That signature activates additional forbidden edges.

[RESULT.md](RESULT.md) proves the exact activation rule, an **all-N deficit-transfer inequality**, and a monotonicity theorem: refining the multiplier signature cannot weaken the bound at fixed smooth cutoff.

## The small demonstration

All rows use the **same eight** `{2,3}`-smooth vertices up to 12. Modulus 1 is the existing multiplier-blind baseline; modulus 5 retains extra divisibility information.

| Variant | Baseline L=1 | Refined L=5 |
|---|---|---|
| k=1 | 11/12 | 317/360 |
| k=2 | 11/12 | 79/90 |
| k=3 | 53/72 | 13/18 |

These are asymptotic upper-bound coefficients arising from the proved finite-N inequality, not densities measured in a finite sweep. **They are weaker than reported literature bounds.** The point is a reusable, rigorously checked refinement at unchanged cutoff, not a record.[8]

## Replay from the repository root

```sh
python3 -I -B experiments/astra-327-fiber-20260912/verify.py --negative-controls
python3 -I -B -m unittest discover -s experiments/astra-327-fiber-20260912 -p 'test_*.py' -v
python3 tools/query_substrate.py for 327
```

Python stdlib only (3.9+). The default verifier reads `receipt.json`, recomputes it, checks all smooth prefixes by direct subset enumeration using the original divisibility predicate, and checks state counts independently by residues. It never rewrites the receipt.

To create a separate receipt explicitly:

```sh
python3 -I -B experiments/astra-327-fiber-20260912/verify.py --emit /tmp/p327-fiber-replay.json
```

Emission refuses to overwrite an existing file. The demo compiler rejects more than 18 smooth vertices, or C/L beyond 10000; these are implementation resource caps, not hypotheses of the mathematical theorem.

## Evidence and scope

- `fiber.py`: activation moduli, exact inclusion–exclusion counts, include/exclude independent-set recurrence, and rational bound.
- `verify.py`: independent subset/residue oracle; identical acceptance gate for normal and poisoned evidence.
- `receipt.json`: fixed k=1,2,3 and L=1,5 cases; 9 graphs, 72 prefixes, witnesses and finite-bound examples.
- `test_fiber.py`, `test_receipt.py`: arithmetic oracles, prime-power states, invalid hypotheses, endpoint behavior, CLI read-only replay, and corrupt-receipt rejection.
- `FRESHNESS.md`, `sources.json`: official banner, separate proof-claim register, literature context, and source pins. No third-party manuscript is bundled.
- `execution.json`: actual local checker, test-suite, and graph-consistency outputs.
- `review.json`: independent automated mathematical/code review outcomes and suggestion dispositions; not human peer review.

The mathematical proof is informal; the finite graph computations are exact and independently replayed. This is not a Lean proof or an independent human review.

## Atlas attachment

Problem node `P327`; surface `S:gap:327:c40419c7`. **No next-cell claim is moved.** The substrate entry describes the transfer method; unit-fraction tag neighbors are candidates only. Production `atlas/graph/`, `views/graph/`, stubs, and frozen certificates are untouched.

## Working question

Can a small collection of activation moduli capture a useful fraction of the constraints lost by the multiplier-blind method, without enlarging the smooth graph? The present example establishes that the gain can be strict. It does not establish the best partition, a competitive bound, or the extremal density.

## Sources

[8] https://leon2k2k2k.github.io/assets/pdf/erdos/erdos327.pdf
