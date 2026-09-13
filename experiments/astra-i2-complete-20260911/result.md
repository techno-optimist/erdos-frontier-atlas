# P699 for \(i=2\): an elementary complete case

**Not a solution of Erdős #699.** Price’s accepted partial proof covers \(j\le 3i/2\) or \(n=2j\). For \(i=2\) that is only \(j=3\) and the central line. This note covers **every** \(3\le j\le n/2\).

Live page 2026-09-11: still FALSIFIABLE / open.

## Theorem

For integers \(n\ge 6\) and \(3\le j\le n/2\),
\[
\gcd\Bigl(\binom n2,\binom nj\Bigr)\ge 2.
\]
Hence some prime \(p\ge 2=i\) divides both binomials.

## Proof

The Pascal identity
\[
j(j-1)\binom nj = n(n-1)\binom{n-2}{j-2}
\]
holds for \(2\le j\le n\). Since \(\binom n2=n(n-1)/2\),
\[
j(j-1)\binom nj = 2\binom n2\binom{n-2}{j-2}.
\]
Let \(g=\gcd(\binom n2,\binom nj)\), \(\binom n2=ga\), \(\binom nj=gb\), with \(\gcd(a,b)=1\). Cancel \(g\):
\[
j(j-1)\,b = 2a\binom{n-2}{j-2}.
\]
Thus \(a\mid j(j-1)b\). Coprimality gives \(a\mid j(j-1)\).

If \(g=1\), then \(a=\binom n2\), so \(\binom n2\mid j(j-1)\). But \(\binom n2>0\) and \(j(j-1)>0\), hence \(\binom n2\le j(j-1)\).

The domain \(j\le n/2\) forbids that: \(2j\le n\) and \(j\ge 3\) give
\[
2j(j-1)\le n(j-1)< n(n-1)=2\binom n2,
\]
the second inequality because \(j<n\). So \(\binom n2>j(j-1)\), contradiction.

Therefore \(g\ge 2\). ∎

No EEES, no Nagura, no localization. The only unformalized sentence in Lean Init is “an integer \(\ge 2\) has a prime factor \(\ge 2\)”.

## Negative control

The tempting strengthening \(\binom n2\mid j(j-1)\) is false at \((n,j)=(6,3)\): \(15\nmid 6\). The proof needs the size bound, not that divisibility.

## Scope

This is the complete \(i=2\) slice of P699 in gcd form. \(i\ge 3\) remains open.
