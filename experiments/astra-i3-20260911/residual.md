# i=3 2-adic residual

**Not a solution of #699.**

## Kernel lemma

If \(3\le j\le n\), \(d\mid\binom n3\), and \(\gcd(d,j!)=1\), then \(d\mid\binom nj\).

Proof: \(d\mid\binom n3\) so \(d\mid n(n-1)(n-2)=6\binom n3\). For \(j\ge 3\), \(n(n-1)(n-2)\) divides \(n^{\underline j}=\binom nj\,j!\). Coprime cancellation against \(j!\) gives \(d\mid\binom nj\).

Axioms `[propext, Quot.sound]`.

## Corollary (informal)

If one of \(n-2,n-1,n\) is a prime \(p>3\), then \(p>j\) (because \(n-2\ge 2j-2>j\)) so \(\gcd(p,j!)=1\), and \(p\mid\binom n3\), hence \(p\mid\binom nj\).

## The only other 2-power route

A 2-power gcd forces the odd part \(o\) of \(\binom n3\) to divide \(j^{\underline 3}\). Hits for \(8\le n\le 1500\):

| n | j | o | gcd |
|---|---|---|---|
| 10 | 5 | 15 | 12 |
| 16 | 7 | 35 | 80 |
| 65 | 15 | 1365 | 1248 |

All three have an odd prime in the gcd.

Every pair with \(8\le n\le 200\) has odd part of \(\gcd(\binom n3,\binom nj)\ge 3\).

## Not proved

\(o\nmid P\) for all \(n>65\). Checked to 1500. Next: bound \(o\) versus \(P\) on all-composite triples, then \(i\ge 4\).
