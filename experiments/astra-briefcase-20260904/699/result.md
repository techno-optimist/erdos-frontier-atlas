# P699: absorb the d=2 wrap by a neighboring-binomial gcd

**Outcome:** an informal proof of the entire line `n=2j+2`, for every `2 <= i < j`, conditional only on the same published EEES theorem used in the existing note. A second argument covers `n=2j+3`, even `i>=4`, except possibly `j=2i-1`. These are mathematical deductions, not conclusions from the finite checks. No novelty, formalization, upstream acceptance, or publication claim. Nothing in the repository or its first proof was changed.

Attachment: `P699`, `S:triage:699`. Read-only baseline: `<atlas checkout>`, HEAD `4831f560255c294474f84bc4b5a815aed86ca83f`.

The [prime-window supplement](diagonal-completion.md) subsequently removes the even-i d=3 diagonal exception and includes i=2. The original checker domains and receipts below remain unchanged.

## The key correction: use a gcd, not shifted integrality

Write `W` for the product of prime powers `q^a || C(n,i)` with `q>=i` and `q` absent from `C(n,j)`.

In the troublesome d=2 case, write

- `i=2A`, `p=i+1=2A+1` prime;
- `j=kp-2` with `k>=2`;
- `B=C(j,A-1)`, `C=C(j+1,A)`;
- `W=p U`, where every prime dividing `U` is at least `i`.

Localization gives `U | B`. Since every prime divisor of `U` is at least `i>A`, we have `gcd(U,A)=1`; from `A C=(j+1)B` it follows that `U | C`. Consequently,

`U <= gcd(B,C) = (B/A) gcd(A,j+1)`.

The equality follows by reducing the fraction `C/B=(j+1)/A`. Now

`gcd(A,j+1) = gcd(A,k-1) <= k-1`,

because `p=2A+1` and `j+1=kp-1`. Thus

`W <= p gcd(B,C) <= p(k-1) B/A < (kp-1)B/A = C`.

The strict inequality is simply `p(k-1)<kp-1`.

This is an exact upper bound despite the fact that `W` need NOT divide `C`. That distinction is what closes the boundary.

## Complete d=2 theorem

**Theorem.** If `2<=i<j` and `n=2j+2`, some prime `q>=i` divides both `C(n,i)` and `C(n,j)`.

Use the already-proved lifted localization lemma from the first note: if `q^a` contributes to `W`, put `M=q^(a+1_{q=i})`, `r=j mod M`, `s=(j+2) mod M`. Then `r+s<i` and `M | E=2+r-s`.

We have `3-i <= E <= i+1`. If `q=i`, then `M>=i^2>i+1`; if `q>i+1`, then `M>=q>i+1`. Therefore these prime powers all have `E=0`. Their residues obey `2r+2<i`, hence

`0<=r<h=ceil((i-2)/2)`.

Each such power divides `B=C(j,h)`, since `h<q`.

The only possible nonzero `E` is `E=p` for `p=i+1` prime, exponent `a=1`. This forces `r=p-2`, `s=0`: from `r-s=p-2` and `r+s<p-1`, necessarily `s=0`. In particular `i` is even and `j=kp-2`, `k>=2`. There is at most one such wrap contribution.

If there is no wrap, `W | C(j,h)` and

`W^2 <= C(j,h)^2 <= C(2j,2h) <= C(n,i)`.

Here `2h<=i<j`, so the last comparison is within the increasing half of the binomial row followed by increasing the top argument. This covers `h=0` too.

If a wrap occurs, the neighboring-binomial gcd argument above gives

`W < C(j+1,i/2)`.

Vandermonde then gives

`W^2 < C(j+1,i/2)^2 < C(2j+2,i) = C(n,i)`.

(The second inequality is strict since the adjacent terms with lower indices `i/2-1` and `i/2+1` are positive.)

If no qualifying common prime existed, `W` would equal the full product `V` of prime powers at primes at least `i` in `C(n,i)`. Write `C(n,i)=uV`, with `u` supported on primes below `i`. EEES gives `u>V` only in its twelve exceptions. Outside them equality is impossible: `gcd(u,V)=1` and `uV=C(n,i)>1`. Hence `u<V` and `C(n,i)<V^2`. Either bound above contradicts this.

The only admissible EEES exceptions on this line are `(n,i,j)=(30,7,14)`, `(36,13,17)`, and `(56,13,27)`. Common primes are respectively `29`, `31`, and `53`, as checked directly. Thus every exception is covered. ∎

The original `i=1` argument is unchanged.

## Additional d=3 subfamily

**Theorem.** If `i>=4` is even, `i<j`, `n=2j+3`, and `j != 2i-1`, then P699 holds for this triple.

Write `i=2A`. Here `q=i` cannot occur because `i>=4` is even. With the same localization, `M | E=3+r-s` and `4-i<=E<=i+2`. Since `i+2` is even, the only possible wrap prime is `p=i+1`, again to exponent one. A wrap forces `r=p-3`, `s=0`: the equations are `r-s=i-2` and `r+s<i`, giving `s=0`. Thus `j=kp-3`, `k>=2`. All other prime powers compress into `B=C(j,A-1)`.

Again `U=W/p` divides both `B` and `C=C(j+1,A)`, with

`gcd(A,j+1)=gcd(A,k-2)`.

If `k>=3`, then

`p gcd(A,k-2) <= p(k-2) < kp-2 = j+1`,

so `W<C`, and `C^2<C(2j+2,i)<C(n,i)` gives the same EEES contradiction. The case `k=2` is exactly `j=2p-3=2i-1`, the excluded diagonal. Without a wrap the original small-binomial bound suffices. The two admissible EEES exceptions in this subfamily are `(n,i,j)=(21,8,9)` and `(33,14,15)`, handled by common primes `19` and `31`, respectively. ∎

A counterexample in this even-i d=3 subfamily is therefore confined to the explicit diagonal `n=4i+1`, `j=2i-1`, with `i+1` prime. This is only a remaining obstruction to this argument, not evidence that these triples violate P699.

## Exact negative examples to tempting stronger steps

1. **False shifted integrality:** `(n,i,j)=(18,4,8)` has absent prime `p=5` to exponent one in `C(18,4)`, but `5` does not divide `C(9,2)=36`. Thus `W | C(j+1,i/2)` is false even at d=2. The proof uses a size bound instead.
2. **False crude size bound:** at `(n,i,j,p)=(42,10,20,11)`,
   - `C(n,i)=1,471,442,973`;
   - `B=C(20,4)=4,845`;
   - `(pB)^2=2,840,357,025 > C(n,i)`.
   The missing factor cannot be paid for by the crude bound. But `C=C(21,5)=20,349`, `gcd(B,C)=969`, and `p gcd(B,C)=10,659<C`.

## Replay and bounded scope

```
python3 -I experiments/astra-briefcase-20260904/699/check_shifted.py
python3 -I experiments/astra-briefcase-20260904/699/check_shifted.py --negative-control
```

The second command must fail. Ordinary replay recomputes and compares `receipt.json`; it never changes the receipt. `--emit` uses exclusive creation.

The checker uses direct integer binomial coefficients to identify absent primes, not the localization formula as its oracle. Domains: d=2, `2<=i<=60`, `i<j<=360`; d=3 additionally restricted to even `i>=4`; plus exact large-j/small-degree inequalities at explicitly listed primes and k values. These are implementation and edge-case checks, not an exhaustive frontier claim.

Actual replay passed: 19,411 d=2 triples (195 wrap cases); 9,512 even-i d=3 probes, including 9,483 in the stated theorem and 16 wrap instances on the excluded diagonal; 54 large-j symbolic-inequality samples; all five admissible EEES exception triples across both theorems. The planted false shifted-integrality control exited 1, as required. Repository status changed during the delegated session because the parent is working concurrently; this child only wrote the three files under `experiments/astra-briefcase-20260904/699/`.

Sources inherited from the read first note:
- Lifted localization and EEES exception table: `experiments/astra-20260904/699-strip.md`.
- EEES original paper: https://users.renyi.hu/~p_erdos/1978-31.pdf
- Accepted Price partial proof: https://www.overleaf.com/read/fptssppkmgpr
- Official status/claim pages: https://www.erdosproblems.com/699 and https://www.erdosproblems.com/forum/thread/699/proof-claims . Read-only fetch still showed the problem open, with one accepted Price partial proof and the later partial claim; it was not a comprehensive novelty search.

Local filesystem paths in this report were normalized for portable publication.
