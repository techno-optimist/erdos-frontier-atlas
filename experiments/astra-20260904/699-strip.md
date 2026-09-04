# P699: an explicit near-central strip

**Status:** an informal all-parameter corollary, with bounded exact computational checks. Not a solution of the full problem, not Lean-formalized, and **no priority claim**. This is a refinement of the prime-power localization in Price / GPT 5.6 Sol Pro's accepted partial proof, using the classical Ecklund–Eggleton–Erdős–Selfridge (EEES) theorem.[11][12][13]

Graph attachment: `P699`, `S:triage:699`, `S:gap:699:6362e233`. Baseline atlas: `0394e3d3b249439ffabec7d96a3311aa441651b8`.[4]

## Result

Let $p_+(i)$ be the least prime strictly larger than $i$. For integers $2\le i<j$, if

$$n=2j+d,\qquad 1\le d\le p_+(i)-i,$$

then some prime $p\ge i$ divides both $\binom ni$ and $\binom nj$.

In particular, **every odd-central triple $n=2j+1$ is covered**. Together with the accepted even-central result, this covers $j=\lfloor n/2\rfloor$ for every admissible $i,n$.[11]

The argument below is a proof using a published theorem, not an inference from a finite search. Freshness checks found this strip neither explicitly in the accepted manuscript nor in the official discussion, but absence from that limited search is not proof of novelty. The newer van Doorn–Rocca manuscript was consulted, not independently certified.[13][14][15]

## 1. Retain the boundary prime power

Suppose $p\ge i$ is prime,

$$a=v_p\binom ni>0,\qquad p\nmid\binom nj.$$

Define $\delta=\mathbf1_{p=i}$ and $M=p^{a+\delta}$. Then the least nonnegative residues

$$r=j\bmod M,\qquad s=(n-j)\bmod M$$

satisfy $r+s<i$.

**Proof.** Among the $i$ consecutive numerator factors $n-i+1,\ldots,n$, at most one is divisible by $p$. Because $a>0$, exactly one is: write it $n-t$ with $0\le t<i$. Also $v_p(i!)=\delta$. Hence $v_p(n-t)=a+\delta$, so $n\bmod M=t$.

Kummer's theorem and $p\nmid\binom nj$ say there are no base-$p$ carries in $j+(n-j)=n$. In particular, there is no carry out of the lowest $a+\delta$ digits, so $r+s<M$. Since $r+s\equiv n\equiv t\pmod M$, we have $r+s=t<i$. ∎

The accepted localization lemma states the conclusion modulo $p^a$. Here the extra factor $p$ when $p=i$ is retained. That is the useful refinement.[11]

## 2. Compress all non-common prime powers

Define

$$W_i(n,j)=\prod_{\substack{p\ge i\ \mathrm{prime}\\p\nmid\binom nj}}p^{v_p(\binom ni)}.$$

This quantity is defined for every triple, not just hypothetical counterexamples. Let

$$h=\left\lceil\frac{i-d}{2}\right\rceil.$$

In the stated strip,

$$\boxed{W_i(n,j)\mid\binom jh.}$$

**Proof.** Bertrand's postulate gives $p_+(i)<2i$, hence $1\le d\le i-1$, $h\ge1$, and $2h\le i$.

For each prime power contributing to $W_i$, use the preceding lemma. Since $n-j=j+d$,

$$M\mid E=d+r-s,\qquad |E|\le d+i-1.$$

If $p>i$, then $M\ge p\ge p_+(i)>d+i-1$. If $p=i$, then $a\ge1$ and $M\ge i^2>2i-2\ge d+i-1$. Thus $E=0$ in either case, giving $s=r+d$.

Now $r+s<i$ implies $2r+d<i$, or $0\le r<h$. Therefore $p^a\mid j-r$ for a factor in $j(j-1)\cdots(j-h+1)$. Distinct prime-power contributions are relatively prime, so their product divides this falling factorial. Since $h<i\le p$, dividing by $h!$ removes none of them. ∎

## 3. Contradict the classical large-prime bound

Write

$$V_i(n)=\prod_{p\ge i\ \mathrm{prime}}p^{v_p(\binom ni)}.$$

EEES proves $\binom ni<V_i(n)^2$ for $n\ge2i$, apart from the twelve pairs listed below. The distinction **primes strictly less than $i$ versus primes at least $i$** is essential; this is the exact version in the original paper.[12]

If our triple had no qualifying common prime, then $V_i(n)=W_i(n,j)$. Compression would give

$$
\binom ni<V_i(n)^2
\le\binom jh^2
<\binom{2j}{2h}
\le\binom{2j}{i}
\le\binom ni,
$$

a contradiction.

The strict middle inequality is Vandermonde: $\binom jh^2$ is one term of the sum for $\binom{2j}{2h}$, and another term is positive because $1\le h$ and $2h\le i<j$. The next inequality is monotonicity up to the center of binomial row $2j$.

### Exceptional pairs, handled directly

The pairs $(9,4)$ and $(10,5)$ have no admissible $i<j\le n/2$. For the others, the following prime lies in $(n-i,n]$ and above $n/2$, so it divides both binomials for every admissible $j$. This is the exceptional-case handling in the accepted proof, replayed here with exact arithmetic.[11][12]

| $(n,i)$ | prime |
|---|---:|
| $(8,3)$ | 7 |
| $(12,5)$ | 11 |
| $(21,7)$ | 19 |
| $(21,8)$ | 19 |
| $(30,7)$ | 29 |
| $(33,13)$ | 31 |
| $(33,14)$ | 31 |
| $(36,13)$ | 31 |
| $(36,17)$ | 31 |
| $(56,13)$ | 53 |

Finally, $i=1$ is elementary: $n\mid j\binom nj$ and $0<j<n$ force $\gcd(n,\binom nj)>1$. ∎

## Computational checks

Run from this directory:

```sh
python3 -I check_699_lemmas.py
python3 -I check_699_lemmas.py --negative-control  # MUST exit nonzero
```

The ordinary run **recomputes**, then compares with `lemma-checks.json`; it never rewrites the receipt. `--emit` is exclusive-create only.

Replayed successfully:

- 1,078,287 non-common prime-power instances for $n\le240$;
- 1,488 of those require the extra boundary power $p=i$;
- 554,659 sharpened Euclidean product divisibilities;
- 18,815 strip compressions, each also checked directly against the binomial gcd condition;
- all 41 admissible exceptional triples;
- 4,704 size comparisons at additional parameter values.

The computations use direct integer binomial coefficients, not the localization identity as an oracle. The negative control deliberately replaces $p^{a+1}$ with $p^{a+2}$ when $p=i$; it fails at $(n,i,j,p)=(18,3,9,3)$. The correct modulus is $9$; the incorrect modulus $27$ gives residues $9,9$, whose sum is not below $3$.

These finite checks validate edge cases and implementation; **the proof of the infinite strip is the argument above, conditional only on the stated published EEES theorem**. It has not been formalized or promoted into the atlas certificate contracts.

## Consequence for search

Combining this strip with the accepted even-central result, any counterexample with $i\ge2$ must obey

$$n-2j\ge p_+(i)-i+1.$$

This is a symbolic pruning rule. We have not modified the frozen sweeper, measured a speedup, or claimed an increased exhaustive cutoff.

## Sources

[4] https://github.com/techno-optimist/erdos-frontier-atlas/tree/0394e3d3b249439ffabec7d96a3311aa441651b8
[11] https://www.overleaf.com/read/fptssppkmgpr
[12] https://users.renyi.hu/~p_erdos/1978-31.pdf
[13] https://www.erdosproblems.com/forum/thread/699/proof-claims
[14] https://www.overleaf.com/read/ywsndhgyrzsx
[15] https://www.erdosproblems.com/forum/thread/699
