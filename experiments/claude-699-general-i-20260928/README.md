# P699 for every i ≥ 3: keep the position, and the exceptional n thin out

**Unpromoted research. An informal proof with exact computational checks.** No novelty or
priority claim, no formalization, and **not a solution of #699**. Graph attachment: `P699`,
`S:triage:699`.

Erdős #699 asks whether for every 1 ≤ i < j ≤ n/2 some prime p ≥ i divides both C(n,i) and
C(n,j). The [i = 3 note](../claude-699-i3-position-20260928/README.md) kept track of *which* of
n, n − 1, n − 2 each prime came from. This note does the same bookkeeping for every i ≥ 3.

- **Theorem 2** turns a counterexample into a small divisibility system.
- **Theorem 3.** For each fixed i, the n that can fail number O(X^(1/3) (log X)^π(i)) up to X.
- **The search** finds no counterexample for i = 4, …, 13 far past the atlas's exhaustive
  all-i sweep, which stops at 10⁸. See the [table](#computation).

## Notation

Fix i ≥ 3. Split every integer x ≥ 1 as x = S·R:
- R, the *rough part*, is the product of the prime powers q^e ‖ x with q > i, or with q = i and
  e ≥ 2;
- S = x/R, the *smooth part*, has only primes below i and at most one factor i.

Call x *smooth* when R = 1. For 0 ≤ t < i write

    n − t = S_t · R_t.

The primes p ≥ i dividing C(n,i) are exactly the primes of R_0 R_1 ⋯ R_(i−1), because
v_p(i!) = [p = i] for p ≥ i. Each such p divides exactly one n − t. Its *block* is
M = p^(v_p(n−t)), the full power of p in R_t.

## Lemma 1 (positional localization)

If p ≥ i divides C(n,i) with block M at position t, and p ∤ C(n,j), then

    j mod M ≤ t,   equivalently   (j mod M) + ((n − j) mod M) = t.        (*)

*Proof.* This is [699-strip.md §1](../astra-20260904/699-strip.md), a refinement of the
prime-power localization in Price's accepted partial proof. Since n ≡ t (mod M), Kummer's
theorem gives no carry out of the lowest v_p(n − t) base-p digits of j + (n − j). ∎

## Theorem 2 (the positional system)

Let i ≥ 3 and i < j ≤ n/2, and suppose no prime p ≥ i divides both C(n,i) and C(n,j). Then
S_0 ≥ 2, and:

- **(a)** R_0 | j. Write j = R_0·m; then 1 ≤ m ≤ S_0/2.
- **(b)** For 1 ≤ t < i, R_t divides P_t(m) = ∏_(r=0..t) (t·m − r·S_0).
- **(c)** 4(n − 1) ≤ S_0² S_1.
- **(d)** If j < n/2, then 6√3·(n − 1)(n − 2) ≤ S_0³ S_1 S_2.
- **(e)** If j = n/2, then R_t = 1 for every odd t < i. In particular n − 1 is smooth.

Conversely, (b) at position t holds exactly when j passes (*) at every block of position t. So
the search below tests (*) itself, not a weakening of it.

*Proof.* Apply Lemma 1 to every block.

**(a)** At t = 0, (*) says M | j. The blocks are powers of distinct primes, so R_0 | j. From
1 ≤ j ≤ n/2 = S_0R_0/2 we get 1 ≤ m ≤ S_0/2, so S_0 ≥ 2.

**(b)** Take a block M at position t ≥ 1, with prime p. Then p ∤ n, since p | n − t and
0 < t < i ≤ p. So S_0 is invertible mod M. Also S_0(j − r) = n·m − r·S_0 ≡ t·m − r·S_0 (mod M).
So M | j − r exactly when M | t·m − r·S_0.

Two factors of P_t differ by (r′ − r)S_0 with 0 < |r′ − r| ≤ t < p, so p divides at most one of
them. Hence M | P_t(m) exactly when M | j − r for some 0 ≤ r ≤ t, which is (*). The blocks at
position t are coprime, so (*) at all of them is the same as R_t | P_t(m).

**(c)** P_1(m) = m(m − S_0), and 0 < m(S_0 − m) ≤ S_0²/4. So n − 1 = S_1R_1 ≤ S_1S_0²/4.

**(d)** Now 1 ≤ m < S_0/2, so Q = m(S_0 − m)(S_0 − 2m) is positive.
- P_2(m) = 2m(2m − S_0)(2m − 2S_0) = 4Q. R_2 is odd, since its primes are at least i ≥ 3, so
  R_2 | Q.
- R_1 | m(S_0 − m), which divides Q.
- R_1 and R_2 are coprime, so R_1R_2 | Q.

Therefore R_1R_2 ≤ Q ≤ S_0³ · max_(0<x<1/2) x(1 − x)(1 − 2x) = S_0³/(6√3).

**(e)** Here m = S_0/2. For odd t each factor is t·m − r·S_0 = (S_0/2)(t − 2r) ≠ 0. A block
prime p is prime to S_0, so p would divide some t − 2r with 0 < |t − 2r| ≤ t < p. That is
impossible, so R_t has no blocks. ∎

For i = 3, (c) and (d) are the size bounds of the i = 3 note, before its parity refinements.

## Theorem 3 (the exceptional n are thin)

For i ≥ 3 let E_i be the set of n for which some j with i < j ≤ n/2 has no common prime p ≥ i.
Then

    #(E_i ∩ [1, X]) = O_i( X^(1/3) · (log X)^π(i) ).

*Proof.* Let Ψ_i(X) be the number of smooth numbers up to X, at most (1 + log₂X)^π(i).
- **A central failure** (j = n/2) needs n − 1 smooth by (e). That gives at most Ψ_i(X) values
  of n.
- **Every other n ∈ E_i satisfies (d).** Fix its smooth parts S_0, S_1, S_2 and put U = S_1S_2.
  - We have gcd(S_0,S_1) = gcd(S_1,S_2) = 1 and gcd(S_0,S_2) | 2. So these n lie in a single
    class modulo lcm(S_0,S_1,S_2) ≥ S_0U/2.
  - By (d), n ≤ 2 + (S_0³U/10)^(1/2).
  - So there are at most 1 + C·min(X/(S_0U), (S_0/U)^(1/2)) ≤ 1 + C·X^(1/3)·U^(−2/3) such n,
    using min(a,b) ≤ a^(1/3) b^(2/3).
  - Sum over the triples of smooth numbers up to X. The total is at most
    Ψ_i(X)³ + C·X^(1/3)·Ψ_i(X)·(Σ_s s^(−2/3))², where s runs over smooth numbers.
  - The sum is finite: it is at most ∏_(p≤i) (1 − p^(−2/3))^(−1). ∎

**Corollary 4 (rational positions).** Suppose a counterexample has j/n = a/b in lowest terms with
3 ≤ b < i. Then n − 1 and n − 2 are both smooth. By Størmer's theorem there are only finitely
many such n for each i.

*Proof.* m = aS_0/b, so b | S_0. For t = 1 and t = 2, each factor of P_t is (S_0/b)(ta − rb).
Take a block prime p ≥ i, which is prime to S_0 and odd. It would have to divide one of:
- a or b − a, both in (0, b); or
- a, b − 2a or b − a, all in (0, b).

Since b < i ≤ p, none of them is divisible by p. So R_1 = R_2 = 1. ∎

## Computation

A counterexample in the i-slice is one of two kinds:
- **central:** n − 1 is smooth and j = n/2;
- **special:** n satisfies (c) and (d), and j = R_0·m with R_1 | P_1(m), R_2 | P_2(m), and
  R_t | P_t(m) for 3 ≤ t < i.

`search699.c` enumerates both exactly up to X.
1. **Special n.** It walks the progressions n ≡ 0 (mod S_0), n ≡ 1 (mod S_1) for all smooth
   S_0 ≥ 2 and S_1, up to min(X, S_0²S_1/4 + 1). The tail of each progression, where (d) needs
   S_2 ≥ 2, is walked through sub-progressions n ≡ 2 (mod d), for the smooth d in (2^k, P·2^k].
   Here P is the largest prime ≤ i. This works because a smooth S_2 > 2^k has its least divisor
   above 2^k in that window. `--plain` walks every element instead.
2. **Candidates.** For each special n it factors R_1 and R_2. Chinese remaindering over their
   blocks gives every m < S_0/2 with R_1 | P_1(m) and R_2 | P_2(m).
3. **Later positions.** It tests R_t | P_t(m) for 3 ≤ t < i by exact modular products. No
   factoring is needed there.
4. **Survivors.** Every survivor with j > i gets the exact test: Kummer carries at every prime
   p ≥ i of C(n,i).

| i | X | special n | (n, m) passing t ≤ 2 | central n | survivors |
|---:|---:|---:|---:|---:|---:|
RESULTS_TABLE

No survivor appears, so **for each i in the table, no counterexample with that i has n ≤ X.**
The i = 3 row repeats the i = 3 note's search to 10¹⁸ through the general bounds. That is a
second route to the same conclusion.

The counts grow like X^(1/3) times a polylog, as Theorem 3 predicts. From 10⁶ to 10¹⁵ the i = 4
count grows about 2.35× per decade and the i = 8 count about 2.7×, against 10^(1/3) ≈ 2.15. Very
few (n, m) survive the first two positions, and none survives the third.

## What remains

- **Larger n** for every i in the table, and **every i ≥ 14**. For fixed i the residual is
  thin (Theorem 3), but no argument here makes it empty.
- **Uniformity in i.** Theorem 3's constant grows with the number of primes below i. The
  prime-gap lemma only confines i to below the gaps near n, which grow with n.
- **Human review and formalization.**

## Replay

```sh
python3 -I experiments/claude-699-general-i-20260928/check_small.py    # ~1.5 min
python3 -I experiments/claude-699-general-i-20260928/verify.py         # pins C to Python; ~2 min
python3 -I experiments/claude-699-general-i-20260928/verify.py --full  # every row of RESULT.json
```

**`check_small.py`**
1. Checks Lemma 1 from the binomial coefficients themselves.
2. Checks every part of Theorem 2 on every pair that passes (*) at the first positions, for
   n ≤ 2500 and i ≤ 10.
3. Checks that the CRT candidates equal direct enumeration on every special n ≤ 2·10⁵.
4. Checks that (b) and (*) agree position by position in 20 million cases.
5. Checks that no pair with n ≤ 3000 passes (*).
6. Runs a **negative control.** With only the positions t ≤ 2 required, 401 pairs do pass for
   i = 4..10, and the search reproduces that brute-force list exactly.

**`verify.py`**
1. Compiles `search699.c` and pins it, in both enumeration modes, to the independent Python
   reference `general.py`: every i = 3..10 up to 10⁸ and i = 11..13 up to 10⁷. The special n are
   compared by an order-independent checksum.
2. Repeats the negative control through the C engine.
3. Checks that sharded runs add up to the unsharded one.
4. Reruns the checkpoint rows of RESULT.json (i ≤ 10 at 10¹¹, i = 11..13 at 10⁹) and the
   frontier windows just above each searched bound.

`--full` reruns every row.

| file | role |
|---|---|
| `nt.py` | exact number theory: proven primality below 3.3·10²⁴, factoring, CRT, Kummer carries |
| `general.py` | the Python reference: blocks, (*), the smooth/rough split, the special-n enumeration and the candidates |
| `search699.c` | the C engine used for the table |
| `check_small.py` | exact small-n checks and the negative control |
| `verify.py`, `run.py` | pinning, sharding, and replay of RESULT.json |
| `RESULT.json` | every run in the table, with checksums and timings |
