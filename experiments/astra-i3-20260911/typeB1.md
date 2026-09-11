# Type B1 is cracked

**Not a solution of #699.** Type B is \(p=P^+(\mathrm{odd\_part}(\binom n3))\le n/4\). Split at \(n/6\):

- **Type B1:** \(n/6 < p \le n/4\), equivalently \(4p \le n < 6p\).
- Type B2: \(p \le n/6\), equivalently \(n \ge 6p\). Still open.

Since \(p \mid n(n-1)(n-2)\), we have \(n\in\{4p,4p+1,4p+2,5p,5p+1,5p+2\}\).
Since \(2p \le n/2 < 3p\), the only \(j\le n/2\) with \(p\mid j(j-1)(j-2)\) are
\[
j\in\{p,p+1,p+2,2p,2p+1,2p+2\}.
\]

## Hits

Global Type B1 scan through \(n=5000\): only \((65,15)\).
Family scans through primes \(p<2000\):

| form | o\|P hits |
|---|---|
| \(n=4p\) | empty |
| \(n=4p+1\) | empty |
| \(n=4p+2\) | empty |
| \(n=5p\) | \((65,15)\) only |
| \(n=5p+1\) | \((16,7)\) (Type A overlap: \(16=2\cdot7+2\)) |
| \(n=5p+2\) | empty |

\((65,15)\): \(p=13\), \(n=5\cdot13\), \(j=15=p+2\), \(\gcd(\binom{65}{3},\binom{65}{15})=1248=32\cdot39\). Odd-prime-bearing.

## Sample gcd bounds (unbounded empty, not a scan)

For even \(n\), \(n-1\mid 3P\). On \(n=4p\) and \(j=2p\):
\[
\gcd(4p-1,\,2p(2p-1)(2p-2))= \gcd(3,p-1),
\]
so \(4p-1\mid 9\). But \(4p-1\ge 11\) for \(p\ge 3\). Empty.
Same bound kills \(j=2p+1\) on \(n=4p\).

For odd \(n=5p\), \(5p-2\mid 3P\). Each of the six \(j\) then forces \(5p-2\) to divide a constant (\(\le 756\)). The only all-composite hit is \((65,15)\).

## Remainder

Type B2: \(P^+\le n/6\). Empty through \(n=10^5\) except no extra beyond \((65,15)\) which is B1. Then \(i\ge 4\).
