# Type B2b leftover (structural)

**Not a solution of #699.** Not another scan of forms \(10p,11p,\ldots\).

## Lemma

Let \(n\ge 6\) be even and \(3\nmid(n-1)\) (equivalently \(n\not\equiv 4\pmod 6\)). Then \(6\mid n(n-2)\), so
\[
n-1 \;\Big|\; \binom n3.
\]
Since \(n-1\) is odd, also \(n-1\mid o=\mathrm{odd\_part}(\binom n3)\). Therefore if \(o\mid j(j-1)(j-2)\) then \(n-1\mid P\).

Proof of \(6\mid n(n-2)\): \(n\) even, so \(n\) and \(n-2\) are consecutive even integers and one is divisible by 4. For 3: \(n\not\equiv 1\pmod 3\), hence \(n\equiv 0\) or \(2\pmod 3\), so \(3\mid n\) or \(3\mid(n-2)\).

## What remains

- Odd \(n\not\equiv 3\pmod 4\) (i.e. \(n\equiv 1\pmod 4\)), already odd-slice empty on \(n\equiv 3\pmod 4\).
- Even \(n\equiv 4\pmod 6\), where \(3\mid(n-1)\) so only \((n-1)/3^\delta\) need divide \(P\) (the (10,5) and (16,7) hits live here: \(10\equiv 4\pmod 6\), \(16\equiv 4\pmod 6\)).
- Even \(n\not\equiv 4\pmod 6\) with \(n-1\) an \((n/10)\)-smooth composite dividing \(P\) (Type B2b).

No further \(m=10,11,\ldots\) family scans. Next method is smoothness of \(n-1\) versus a 3-consecutive product, or the odd \(n\equiv 1\pmod 4\) 2-adic count.
