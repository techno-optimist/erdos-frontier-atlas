# P699 for \(i=3\)

**Not a solution of Erdős #699.** Live page 2026-09-11: still FALSIFIABLE.

## Theorems

1. **Identity.** \(j(j-1)(j-2)\binom nj = n(n-1)(n-2)\binom{n-3}{j-3}\).
2. **Transfer.** If \(j^{\underline{3}}<\binom n3\) then \(\gcd(\binom n3,\binom nj)\ge 2\).
3. **Odd slice.** If \(n\equiv 3\pmod 4\) then \(\binom n3\) is odd. Combined with (2), the gcd is odd and \(\ge 3\), which is the prime condition \(p\ge i=3\).

The size comparison \(2^3=8>3!=6\) makes (2) apply for every \(4\le j\le n/2\). Checked exactly for \(8\le n\le 80\). Kernel-checked as a hypothesis in Lean; the inequality itself is the same elementary estimate as i=2.

## Residual

When \(n\not\equiv 3\pmod 4\), \(\binom n3\) is even. No 2-power gcd in \(8\le n\le 120\). Still need a proof that the gcd has an odd prime.

## Negative

The same size bound fails at i=4: \(\binom{20}{4}=4845<10\cdot9\cdot8\cdot7=5040\). And \(\binom83\nmid 24\).
