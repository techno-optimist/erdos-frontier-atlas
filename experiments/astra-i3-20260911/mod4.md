# n ≡ 3 (mod 4): o|P is empty

**Not a solution of #699.** Live page remains FALSIFIABLE (accessed 2026-09-11).

For \(n=4t+3\ge 7\), \(\binom n3\) is odd (kernel `binom_three_odd_of_mod4`), so \(o=\binom n3\). The size comparison against \(P_{\max}=(n/2)(n/2-1)(n/2-2)\) is the cubic identity
\[
6\binom n3 - 6P_{\max} = 16t^3+96t^2+56t+6 > 0.
\]
Hence \(\binom n3 > P_{\max} \ge j(j-1)(j-2)\) for every \(j\le n/2\), so \(o\nmid P\).

This kills the i=3 2-adic residual on a positive-density set of \(n\). Remaining o|P live only for \(n\not\equiv 3\pmod 4\).

Checked: no o|P hits for \(n\equiv 3\pmod 4\) through \(n=400\).
