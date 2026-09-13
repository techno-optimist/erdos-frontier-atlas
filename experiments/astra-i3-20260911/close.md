# Closing i=3 (gcd form)

**Not a full solution of #699.** Live #699 remains FALSIFIABLE.

## Infinite families, kernel-checked

1. `cancel_coprime_fac`: \(d\mid\binom n3\) and \(\gcd(d,j!)=1\) \(\Rightarrow d\mid\binom nj\).
2. `coprime_six_cancel`: if \(\gcd(n,6)=1\) and \(\gcd(n,j!)=1\) then \(n\mid\binom n3\) and \(n\mid\binom nj\).

In particular if \(n>3\) is prime then \(\gcd(n,6)=1\) and \(n>j\) so \(\gcd(n,j!)=1\), hence a prime \(p=n\ge 5>j\) divides both binomials.

The same cancel applies to any prime \(p\in\{n-2,n-1,n\}\) with \(p>3\): such a \(p\) exceeds \(j\le n/2\).

## The 2-power route

A 2-power gcd forces \(o\mid j^{\underline 3}\) with \(o\) the odd part of \(\binom n3\).

Split on \(p=P^+(o)\):

- **Type A**, \(p>n/4\). Then \(2p>n/2\), so \(j\in\{p,p+1,p+2\}\).
  - \(n=2q\) with \(q\) prime: only \(j=q\), and \(2q-1\mid 3(q-2)\) forces \(q=5\), pair \((10,5)\). **Proved.**
  - Otherwise: \((16,7)\) is the only other type A hit through \(n=20000\).
- **Type B**, \(p\le n/4\). Only \((65,15)\) for \(8\le n\le 100000\). (Also \((16,7)\) is type A.)

The three \(o\mid P\) pairs have gcds \(12,80,1248\), all odd-prime-bearing.

## Not proved

Type B empty for all \(n>65\). Type A empty except \((10,5)\) and \((16,7)\). Those are checked to the bounds above, not kernel-checked.

Then \(i\ge 4\).
