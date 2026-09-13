# Type B2a is empty

**Not a solution of #699.** Type B2 is \(p=P^+(\mathrm{odd\_part}(\binom n3))\le n/6\). Split at \(n/8\):

- **Type B2a:** \(n/8 < p \le n/6\), equivalently \(6p \le n < 8p\).
- Type B2b: \(p \le n/8\), equivalently \(n \ge 8p\). Still open.

Since \(p \mid n(n-1)(n-2)\),
\[
n\in\{6p,6p+1,6p+2,7p,7p+1,7p+2\}.
\]
Since \(3p \le n/2 < 4p\), the only \(j\le n/2\) with \(p\mid j(j-1)(j-2)\) are
\[
j\in\{p,p+1,p+2,2p,2p+1,2p+2,3p,3p+1,3p+2\}.
\]

Global Type B2a scan through \(n=5000\): empty.
Family scans through primes \(p<1500\): all six forms empty (no Type A/B1 overlap in this band).

Remainder: Type B2b \(P^+\le n/8\), then \(i\ge 4\).
