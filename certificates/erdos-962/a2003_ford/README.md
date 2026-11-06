# OEIS A327909(2001..2003): the next three cells

**A327909(2001) = A327909(2002) = 1550254764943, and A327909(2003) = 1575356265925.**
This is an exact OEIS-term receipt, not a formal certificate and not an advance on the
asymptotic Erdős #962 growth question. Confidence is about 7/10: ordered computation,
independent witness factorization and replayable controls rather than a formal proof.

## Prior plateau, n = 2001 and 2002

Let `s0 = 1550254764943`. The frozen `RESULT_ford_2000.json` records `a(2000) = s0`
with a maximal run of 2002 integers. No prime separates 1999 and 2003, so n = 2000,
2001 and 2002 use the same smoothness class. The run at `s0` gives `a(n) <= s0` for
those three n, while the prefix `a(n+1) >= a(n)` of any valid run gives the reverse
inequality. The prior one-cell boundary therefore covers exactly three cells:
`a(2000) = a(2001) = a(2002) = s0`. `verify_ford_2003.py` rechecks this run directly.

## New ordered-search cell, n = 2003

2003 is prime. The archived `probe.py.src.txt` source marks exact 2003-smooth integers in increasing
order, beginning at `s0`, with `W = 10^11`. It found the first qualifying start at
1575356265925 after 19328.662 s (about 5h22m). The source window is `(s0, s0+10^11]`.
The reported neighbouring smooth integers are 1575356265924 and 1575356268128, leaving
a run of 2203 integers. This is an ordered forward probe, not a new full `[1,X]` table
or a full `runs.c` scan. There is deliberately no fabricated full-table result file; the adjacent single-term manifest is explicitly `not_a_full_table`.

The archived independent `check.py.src.txt` source factors all 2003 witness integers with `sympy` as
well as trialling the smoothness class. Its planted offset-0 failure is rejected. The
standalone `verify_ford_2003.py` rechecks the entire 2203-run and both boundaries by
repeated gcd division, recomputes the a(2001..2002) plateau from the frozen a(2000)
receipt, checks the source hashes, and rejects two shifted starts, a short prior
witness and a deliberately damaged witness. Its stdlib-only fast replay passed on
2026-11-06; see `VERIFY.txt`.

```sh
python3 -I certificates/erdos-962/a2003_ford/verify_ford_2003.py
# {"witness_and_boundaries_2003":true,"prior_plateau_2001_2002":true,"minimality_replayed":false}
```

The default replay does not claim to regenerate minimality: it verifies the witness,
prior exact cells and receipt. Minimality comes from the original ordered probe. For
an expensive, explicit ordered-search audit, run the same command with
`--replay-search`. The publishing pass did not invoke that mode and did not rerun
any search. The optional mode requires `verified_2003:true` only if all checks and
the newly ordered-found start agree.

## Evidence

`RECEIPT_collect_W1e11_1106.txt` (SHA-256
`384af3ee37b9aee04a3780a0398da06d5bed353ea753020a7013bd0b9427c245`),
`FALSIFIER.txt`, the search tail, original independent-checker outputs and
`libsmooth.py` remain unchanged. `RECEIPT_prior_2001_2002.txt` is a clearly marked
public excerpt of the earlier Ford plateau receipt, with its source hash recorded.

Original `probe`/`check` source text is preserved byte for byte as `.py.src.txt`.
Neither is a Python replay entrypoint:
the originals predate the repository's `python -I` sibling-import rule.
`probe_ford_2003.py` and `check_ford_2003.py` are tiny public runners that enable
isolated imports and `runpy.run_path` for the text-pinned originals; they do not
reimplement the algorithms or change evidence interpretation. Their hashes, the
source hashes and the verifier's hashes are pinned in the `promoted` contract in
`certificates/contracts.json`. Here `promoted` is the public-receipt publishing
status, not a claim that the fast replay certified minimality.

The next cell is open: `A327909(2004) >= A327909(2003)`, by the same prefix
monotonicity. No value beyond a(2003) is claimed. The OEIS b-file was reported to end
at n=999 in the earlier receipt; no new OEIS submission is represented here.
