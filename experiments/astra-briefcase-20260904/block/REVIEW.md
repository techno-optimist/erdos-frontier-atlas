# Independent adversarial review

## Verdict

**No mathematical gap found in the stated Laurent-block theorem.** The induction and finite base coverage are complete for positive integer r,s,t; the shifted-scalar identity legitimately extends the result to all real c,d,e >= 1. This is an informal mathematical review, not a formalization or a result about tree log-concavity.

The audited definition is `B` in `check.py:24-25`, independently matched there with the active-run construction at lines 26-37. The external supplied `993-block.md` was not present in this bundle and was not checked for correspondence.

## Main adversarial checks

- **Binomial margin (`RESULT.md:34-44`).** The Pascal recurrence is valid. For j=2 the other summand is D(N-1,1), which is nonnegative. At a new even center j=N/2, the formally extended binomial difference D(N-1,j) is zero, while D(N-1,j-1) is within the preceding row's interior and is at least 14. Thus the center does not leave an induction hole. Minor notation: D is initially defined only through floor(N/2), so explicitly allowing its binomial formula outside that range would make the even-center sentence fully literal.
- **Single-P induction (`54-74`).** With N>=8 and a>=2, the exact identity factors out w and replaces (N,a,b) by (N-1,a-1,b). The inequalities and parity are preserved. Descent necessarily reaches a=1 or N=7, not an unhandled N<7 case. At a=1, b=0,1 are separately CU; for b>=2 the perturbation has coefficient at most one and no first-edge decrease. The N=7 table contains every admissible pair exactly once.
- **Double-P induction (`76-104`).** Descent replaces s by s-1 and N by N-1, keeping r,t positive, and ends at s=1 or N=7. At s=1 the lower pair can overlap the upper pair only when min(r,t)=1, and then only at N-2. When |r-t| is zero or one, the central multiplicity is two but cannot overlap the outer pair because r+t>=6. Thus coefficient bound two and absence of a first-edge decrease both hold. The N=7 table contains every positive triple exactly once.
- **Coverage and unit block (`106-139`).** The isolated spike cannot lie at an outer exponent; exponent zero or one only raises the center. Each of the seven terms satisfies its claimed majorant's parity and degree constraints. Their average is exactly the unit block. The small-block table covers all positive triples with total degree 3 through 6, with no symmetry reduction hiding an orientation.
- **Real scalars (`141-162`).** Q_j is CU for every positive integer j, including j=1,2. Q_a Q_b has edge coefficient four; subtracting P_(a+b) lowers only the two outer coefficients to three and preserves nonnegativity and inward monotonicity. All shifted coefficients have parity N. The multilinear expansion is correct, so no sampling or integrality assumption is used in extending to real scalars.

## Executed verification

1. `python3 -I experiments/astra-briefcase-20260904/block/check.py --bound 24` exited 0: 13,824 blocks, no failures or ties, 192 state identities, 216 shifted-scalar identities, and the stated negative control rejected.
2. `python3 -I experiments/astra-briefcase-20260904/block/review_check.py` exited 0. This new stdlib checker does not import the reviewed implementation. It:
   - reruns the original checker and compares its full JSON with `receipt.json`;
   - independently constructs the admissible parameter sets and verifies exact coverage: 16 single-P, 15 double-P, 20 small-block cases;
   - parses all displayed tables and checks exact agreement with the replay;
   - recomputes majorant bases by repeated convolution, rather than binomial coefficients;
   - recomputes every small block by direct enumeration of signs of free w factors and active runs;
   - verifies the shifted identity exactly in a formal Laurent ring, treating z^r,z^s,z^t,W_r,W_s,W_t,C,D,E as independent symbols (50 resulting monomials);
   - diagnostically checks the margin for 94 rows, 2,444 a=1 single-P cases, and 4,841 s=1 double-P cases through N=100.

The supplementary finite diagnostics are not substitutes for the unbounded arguments above.

## Nonblocking checker limitations

`failures()` (`check.py:38-41`) checks symmetry and inward inequalities but not nonnegativity or single-parity support. Actual replay showed it returns an empty failure list for both `{-2:-1,0:-1,2:-1}` and `{-2:1,-1:4,0:2,1:4,2:1}`. This is **not a gap in the present theorem or finite bases**: the expressions checked there have nonnegative, single-parity coefficients by construction, and the independent review checker explicitly tests both conditions. For a reusable CU gate, add those tests and an empty-polynomial policy.

The original checker relies on Python assertions; use the documented `python3 -I` invocation without `-O`. The program computes the complete boundary sets but does not explicitly assert their declared cardinalities; the independent checker now does so. Its finite scalar substitutions alone would not establish the general identity; the written algebra and new exact symbolic check do.

## Artifacts and scope

Created `review_check.py` and this `REVIEW.md`. Left `RESULT.md`, `check.py`, and `receipt.json` unchanged. No repository, external service, or publication state was changed. Global combinatorial partition and connector/outside-factor obligations remain outside this review.

Local paths normalized for publication; third-party reading copies are not bundled.
