# Independent adversarial review: P699 neighboring-binomial argument

## Verdict

**PASS as an informal mathematical proof, using the published EEES theorem.** I found no mathematical gap in either (a) the complete `n=2j+2`, `2<=i<j` result, or (b) the even-`i>=4`, `n=2j+3`, `j!=2i-1` result. No changes to the submitted argument or repository were made. This is not formal verification, a novelty assessment, or an upstream acceptance claim.

Reviewed sources: `experiments/astra-briefcase-20260904/699/result.md`, its checker/receipt, and the full inherited localization/EEES argument in `experiments/astra-20260904/699-strip.md`. The original EEES paper was fetched and its printed main theorem on p.258 visually checked, rather than trusting its damaged PDF text extraction.

## Critical mathematical checks

1. **Lifted localization is sound.** For prime `q>=i`, an `i`-term numerator contains at most one multiple of `q`. If `a=v_q(C(n,i))>0`, that multiple has valuation exactly `a+1_{q=i}`, because `v_q(i!)=1_{q=i}`. Thus `n mod M=t<i` for `M=q^(a+1_{q=i})`. Kummer's no-carry criterion, from `q` absent in `C(n,j)`, gives `r+s<M`; consequently `r+s=t<i`. The extra boundary power is essential and correctly retained.

2. **Wrap classification is exhaustive.** With `E=d+r-s`, `d-i+1<=E<=d+i-1` and `M|E`. For `d=2`, no negative nonzero multiple of `M` fits. The `q=i` case has `M>=i^2>i+1`; all `q>i+1` are also excluded. The only possible nonzero case is `q=i+1=p`, `a=1`, `E=p`, with `r=p-2,s=0`. For even `i>=4,d=3`, `q=i` is impossible, `i+2` is composite, and the same reasoning leaves only `p=i+1,a=1,r=p-3,s=0`. The strict condition `r+s<i` correctly rules out `s=1` in the latter case.

3. **Nonwrap compression preserves whole prime powers.** `E=0` gives `2r+d<i`, hence `r<h=ceil((i-d)/2)`. Since `h<i<=q`, dividing the falling factorial by `h!` removes none of the needed prime powers. This handles `i=2,d=2,h=0`: there can be no nonwrap contribution, so `W=1` in the no-wrap case. The comparison `W^2<=C(n,i)` suffices to contradict the strict EEES bound; no unjustified strict Vandermonde inequality at `h=0` is needed.

4. **The adjacent-binomial gcd step is valid, not an integrality mistake.** Let `B=C(j,A-1)`, `C=C(j+1,A)`; then `A*C=(j+1)*B`. All prime divisors of `U=W/p` are at least `i>A`, so `gcd(U,A)=1` and `U|B` implies `U|C`. Reducing `(j+1)/A` gives the exact identity `gcd(B,C)=B*gcd(A,j+1)/A`. Therefore `W<=p*gcd(B,C)`, without claiming `W|C`.

5. **Both wrap inequalities close exactly the claimed domains.** For `d=2`, `j=kp-2`, `k>=2`, and `gcd(A,j+1)=gcd(A,k-1)<=k-1`; hence `p*gcd(A,j+1)<j+1`. This includes `A=1`. For `d=3`, the gcd is `gcd(A,k-2)` and the argument works for `k>=3`. At `k=2`, this gcd is `A`, so that estimate genuinely stops working. This is precisely `j=2i-1`. Diagonal cases with composite `i+1`, or without an actual absent wrap prime, are already covered by the no-wrap argument. No counterexample on the remaining diagonal is asserted.

6. **The final size contradiction is sound.** The shifted binomial has lower index `A` and top `j+1>A`; the additional Vandermonde terms are positive. Thus `W<C` implies `W^2<C(2j+2,i)`, and increasing the top gives the required `d=3` bound. Under the hypothetical absence of a common prime at least `i`, the defined absent-prime product `W` equals the full large-prime product `V`.

7. **EEES is used with the correct cutoff and complete exception handling.** The original theorem has `n>=2i`, small primes `<i`, and large primes `>=i`, with exactly the twelve pairs in the inherited note. Its wording is `u>v` in exactly those cases; outside them equality is impossible here because `gcd(u,v)=1` and `uv=C(n,i)>1`, so `C(n,i)<V^2` follows. The only admissible exception triples are exactly the three listed for `d=2` and two for the stated `d=3` family. The author's primes `29,31,53,19,31` were directly checked to divide both binomials in their respective triples.

## Execution evidence

- Author checker replay: exit **0**; its receipt reproduced exactly.
- Author false-shifted-integrality control: exit **1**, for the advertised assertion.
- New independent checker: exit **0**. It uses exact binomials and independently compares prime valuations with Legendre factorial valuations.
- Independent line checks: **132,542 distinct triples**; **132,438** in the stated theorem domains, plus **104** excluded diagonal probes. Exhaustive `j<=420` and all applicable `i<j`, plus 1,500 deterministic extra draws (`seed=699`, `421<=j<=1600`, `i<=700`). All theorem cases had a directly verified qualifying common prime. All 104 diagonal probes also had such a prime; this is only bounded evidence.
- Line checks included **1,386,171** absent-prime-power contributions, **90** boundary-prime contributions, and **461** contributions with exponent at least two.
- Independent general localization checks: **66,729 triples** with `n<=120`, covering **76,106** absent-prime-power contributions, including **377** boundary-prime contributions.
- Direct large-prime-product enumeration through `n=120` found precisely the twelve printed EEES exceptions. This verifies transcription/implementation, not the published all-parameter theorem.

Receipt: `independent-receipt.json`. Deterministic line-record digest: `739e841cb32075b43639cdab41775f9e8161af1260df8ce81b22c8206f116728`.

## Optional editorial / checker hardening

No mathematical correction is required. For readability, explicitly add `gcd(U,A)=1` at the cancellation step and the one-line exclusion of equality in the EEES invocation. The author's fixed prime list below 1500 is sufficient for its present direct-check domain (`n<=723`), but should be made dynamic or range-guarded before widening that domain. Its negative control is an explicit false-identity check, not a general robustness test of receipt validation.

## Local files

Created only under `experiments/astra-briefcase-20260904/699/`: this report, `independent_check.py`, `independent-receipt.json`, a reading copy `EEES-1978.pdf`, and its page-258 rendering. The initial rendering attempt lacked Pillow; an isolated `uv --with pillow` retry succeeded. PDF SHA-256: `a9c060afbd03a56db5c0ccc9432e0a03ff30a75e6fca0e3ebaea85bee47a768d`.

Source: https://users.renyi.hu/~p_erdos/1978-31.pdf (1978, pp.257–269).
Replay: `python3 -I experiments/astra-briefcase-20260904/699/independent_check.py` (without `--emit`; ordinary execution does not overwrite the stored receipt).

Local paths normalized for publication; third-party reading copies are not bundled.
