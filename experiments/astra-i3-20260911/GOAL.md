# Campaign working doc

Not a solution of #699 or #376. Live #699 remains FALSIFIABLE; live #376 remains OPEN.

## North star

The atlas is a **method substrate and strike map**, not a solution scoreboard.

Famous problems are landmarks for *methods* — lemmas, remaining obligations, transferable operators — then a long digestion, not a planted flag. That is the same misalignment the 2026-09-11 Tao/Fields declaration names for lab incentives; at this repo’s scale it means: do not farm a known OEIS prefix to a larger cutoff (A030979 through \(3^{24}\), \(3^{31}\), \(3^{35}\) was that failure). Thompson already enumerated to \(10^{70}\). Completeness of a known list is not a crack.

**Do:** kernel or exact-arithmetic lemmas; explicit remaining gaps; operators other problems can query; official-status overlays; production `atlas/graph/` frozen.

**Don’t:** claim an Erdős solution; silently rewrite cards; double a computational cutoff because “keep at the wheel” was said.

PRs 150–152 stay as a bounded replay of A030979(1..43). Do not extend \(D\).

## P699 by i, then stop pretending the size bound works forever

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
| 3 | Type A+B1+B2a; n≡3 (mod 4) residual empty; band 8–9 empty | Type B2b: consecutive \((n/10)\)-smooth leftover, not another band scan |
| ≥ 4 | size bound dead | primes, EEES, localization |

## i=3 leftover (structural)

Kernel `cancel_coprime_fac`: if \(d\mid\binom n3\) and \(\gcd(d,j!)=1\) then \(d\mid\binom nj\).

If the gcd were a 2-power then \(o=\mathrm{odd\_part}(\binom n3)\) would satisfy \(o\mid j(j-1)(j-2)\). Hits with an odd prime: (10,5), (16,7), (65,15).

Type B2b (\(P^+(o)\le n/10\)) is not “scan m=10,11,…” forever. Remaining n have \(n,n-1,n-2\) free of odd primes \(>n/10\). For even n with \(3\nmid(n-1)\), \(n-1\mid P\).

## #376 leftover (idea, not search)

Kummer: \(\gcd(\binom{2n}n,105)=1\) iff restricted digits in bases 3,5,7. EGRS 1975 already does any two odd primes. The wall is infinitude for three primes. Next method is a pumping/automaton argument, not \(D=36\).
