# Campaign: crack P699 by i, then stop pretending the size bound works forever

Not a solution of #699. Live page remains FALSIFIABLE.

## Why this cut

The Pascal identity
\[
j^{\underline{i}}\binom nj = n^{\underline{i}}\binom{n-i}{j-i}
= i!\binom ni\binom{n-i}{j-i}
\]
plus coprime cancellation says: if \(\gcd(\binom ni,\binom nj)=1\) then \(\binom ni\) divides \(j^{\underline{i}}\).
On \(j\le n/2\) the size comparison \(\binom ni > j^{\underline{i}}\) is
\[
\frac{n^i}{i!} \;\text{vs}\; \Bigl(\frac n2\Bigr)^i
\qquad\text{i.e.}\qquad 2^i > i!.
\]
That inequality holds **only for \(i\le 3\)**. So i=2 and i=3 are the last elementary slices. i=4 already fails the bound (\(20,j=10\): \(4845<5040\)).

| i | Status | What's left |
|---|---|---|
| 2 | kernel-checked gcd ≥ 2 for every pair | prime-factor Init gap only |
| 3 | Type A+B1+B2a; n≡3 (mod 4) residual empty; band 8–9 empty | n≢3 (mod 4) and P+≤n/10 |
| ≥ 4 | size bound dead | primes, EEES, localization |

## This lane's theorem

For \(4\le j\) and \(2j\le n\),
\[
\gcd\Bigl(\binom n3,\binom nj\Bigr)\ge 2.
\]
If additionally \(n\equiv 3\pmod 4\), then \(\binom n3\) is odd, so the gcd is odd and therefore \(\ge 3\). That is the i=3 prime condition on a positive-density set of n.

## Residual (this crack)

Kernel lemma `cancel_coprime_fac`: if \(d\mid\binom n3\) and \(\gcd(d,j!)=1\) then \(d\mid\binom nj\). So any factor of \(\binom n3\) made of primes \(>j\) also divides \(\binom nj\). In particular if \(n-2\), \(n-1\), or \(n\) is a prime \(>3\), that prime is \(>j\) and we are done.

If the gcd were a 2-power then the odd part \(o\) of \(\binom n3\) would be coprime to \(\binom nj\), hence \(o\mid j(j-1)(j-2)\). That divisibility holds only at **(10,5), (16,7), (65,15)** for \(8\le n\le 1500\), and those three gcds are 12, 80, 1248 — all with an odd prime. Exact check: every pair \(8\le n\le 200\) has odd part of the gcd \(\ge 3\).

See `close.md`. Type B \(o\mid P\) only at \((65,15)\) through \(n=10^5\). \(n=2p\) only \((10,5)\).
