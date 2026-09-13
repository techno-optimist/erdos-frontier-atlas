# Type A is cracked

**Not a solution of #699.** If \(o=\mathrm{odd\_part}(\binom n3)\) and \(p=P^+(o)>n/4\), then \(2p>n/2\ge j\), so \(o\mid j(j-1)(j-2)\) forces \(j\in\{p,p+1,p+2\}\).

Since \(p\mid n(n-1)(n-2)\) and \(n<4p\),
\[
n\in\{p,2p,3p,\;p+1,2p+1,3p+1,\;p+2,2p+2,3p+2\}.
\]
The three \(m=1\) rows have a prime in \(\{n-2,n-1,n\}\) and fall under `cancel_coprime_fac`.

## \(n=2p\)

Only \(j=p\). Then \(o=p(2p-1)\mathrm{Odd}(p-1)/3\) and
\[
(2p-1)\mathrm{Odd}(p-1)\mid 3(p-1)(p-2).
\]
\(2p-1\) is odd, hence \(2p-1\mid 3(p-2)\). The only prime solution of \(2p-1=3(p-2)\) is \(p=5\): pair \((10,5)\). For multiplier \(\ge 2\), \(2(2p-1)>3(p-2)\).

## \(n=2p+2\)

\(j\in\{p,p+1\}\). \(\gcd(2p+1,p+1)=1\), so \(2p+1\mid 3(p-1)(p-2)\). Writing \(d=2p+1\) gives \(d\mid 45\), hence \(p=7\): pair \((16,7)\). The slot \(j=p+1\) forces \(2p+1\mid 3(p-1)\), no prime solutions.

## \(n=2p+1\)

Only \(j=p\). \(\gcd(2p+1,2p-1)=1\), so \(2p+1\mid 3(p-1)(p-2)\), again \(d\mid 45\), and those \(n\) have a prime in the triple (Case 1). No all-composite hits.

## \(n=3p\)

\(\gcd(3p-2,p-1)=1\). For \(j=p\), \(3p-2\mid(p-2)\), but \(3p-2>p-2\). For \(j=p+1\), \(3p-2\) never divides \(p^2-1\). For \(j=p+2\), \(3p-2\mid 40\) and is never \(0\bmod 3\), no prime \(p\). Empty.

## \(n=3p+1\) and \(n=3p+2\)

These overlap the known hits: \(10=3\cdot 3+1=2\cdot 5\), \(16=3\cdot 5+1=2\cdot 7+2\). Family search through \(p<2000\) finds no others. Type A scan of all \(n\le 5000\) finds only those two.

## Residual

Type B: \(P^+(o)\le n/4\). Only \((65,15)\) through \(n=10^5\). That is the last unproved infinite class for i=3.
