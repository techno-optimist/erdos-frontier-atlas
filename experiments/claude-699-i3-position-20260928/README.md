# P699, i = 3: keep the position, and the odd n fall away

**Unpromoted research. An informal proof with exact computational checks.** No novelty or
priority claim, no formalization, and **not a solution of #699**: the i = 3 slice is still
open at the residual described below. Graph attachment: `P699`, `S:triage:699`.

Erdős #699 asks whether for every 1 ≤ i < j ≤ n/2 some prime p ≥ i divides both C(n,i) and
C(n,j). The i = 3 campaign ([GOAL](../astra-i3-20260911/GOAL.md)) left a residual. Its
[structural split](../astra-i3-20260911/typeB2b.md) lists three open branches: n ≡ 1 (mod 4),
n ≡ 4 (mod 6), and n − 1 with at least two distinct odd primes.

This note closes every odd n and every n ≡ 2 (mod 4). In particular it closes the n ≡ 1 (mod 4)
branch and the n ≡ 10 (mod 12) half of n ≡ 4 (mod 6). The remaining i = 3 cases are pushed into
a thin family of n that are nearly powers of two. An exact search clears that family up to 10¹⁸.

## The idea: positional localization

The campaign works with `odd_part(C(n,3)) | j(j−1)(j−2)`. That condition forgets which of
n, n − 1, n − 2 each prime came from, and the position is what matters.

**Lemma (positional localization).** Let q be an odd prime dividing C(n,3). Let t ∈ {0,1,2} be
the position with q | n − t, and put M = q^{v_q(n−t)}. Here q = 3 divides C(n,3) only when
v₃(n − t) ≥ 2. If q ∤ C(n,j), then

    (j mod M) + ((n − j) mod M) = t.                                        (*)

So j ≡ r (mod M) with 0 ≤ r ≤ t: a prime power from n divides j itself; one from n − 1 divides
j or j − 1; one from n − 2 divides j, j − 1 or j − 2.

*Proof.* This is the i = 3 case of the localization in [699-strip.md
§1](../astra-20260904/699-strip.md), itself a refinement of the prime-power localization in
Price's accepted partial proof.
- Exactly one of n, n − 1, n − 2 is divisible by q, and v_q(C(n,3)) = v_q(n − t) − [q = 3], so
  n ≡ t (mod M).
- Kummer: q ∤ C(n,j) means no carry in base q when adding j and n − j. In particular nothing
  carries out of the lowest v_q(n − t) digits, so the two residues sum to n mod M = t. ∎

## Theorem

Let 3 < j ≤ n/2, and suppose no prime p ≥ 3 divides both C(n,3) and C(n,j). Write
n = 2^a · 3^ε · A with A odd and ε = 1 exactly when 3 ‖ n, so A is prime to 3 when ε = 1. Put
K = 2^(a−1) · 3^ε. Then:

1. **4 | n.** No odd n and no n ≡ 2 (mod 4) is a counterexample.
2. **j = A·m with 1 ≤ m < K.** Put B = (n − 1)/3^[3‖n−1] and
   C = (n − 2)/(2 · 3^[3‖n−2]). Every prime power exactly dividing B divides m or 2K − m. Every
   one exactly dividing C divides m, K − m or 2K − m.
3. **(2KA − 1)(2KA − 2) ≤ (4/√3)·K³.** Hence A < 0.76·√K + 1: the odd part of n, after removing
   a lone 3, is at most about 0.66·n^(1/3).

### Proof

Apply (*) to every odd prime of C(n,3); each is assumed not to divide C(n,j).

**Primes of n (t = 0).** Here r = 0, so M | j. The product of these M is the odd part of n,
except that a lone factor 3 contributes nothing. That product is A, so **A | j**.

**Odd n.** Then A ∈ {n, n/3}, and 0 < j < n forces A = n/3, j = n/3 and 3 ‖ n. Now n − 2 ≥ 5 is
odd and prime to 3. Take any prime q | n − 2 with M = q^{v_q(n−2)} ≥ 5. Then r = j mod M is in
{0, 1, 2}, and 3j = n ≡ 2 (mod M) gives M | 3r − 2 ∈ {−2, 1, 4}. That is impossible, so
q | C(n,j), a contradiction.

**Even n.** Write j = A·m. Since j ≤ n/2 = KA, we have 1 ≤ m ≤ K, and gcd(A, BC) = 1.
- A prime power M of B (t = 1) has r ∈ {0, 1}. If r = 0 then M | j, so M | m. If r = 1 then
  M | n − j = A(2K − m), so M | 2K − m.
- A prime power M of C (t = 2) has r ∈ {0, 1, 2}.
  - r = 0 gives M | m.
  - r = 2 gives M | n − j, so M | 2K − m.
  - r = 1 gives M | j − 1. Because M | (n − 2)/2 = KA − 1, we have j − 1 ≡ j − KA = −A(K − m)
    (mod M), so M | K − m.

**The central case m = K**, where j = n/2. Both options put every prime power of B inside
K = 2^(a−1)·3^ε. But B is odd, and prime to 3 whenever 3 | K, so B = 1 and n − 1 ∈ {1, 3}. That
leaves no admissible j.

**n ≡ 2 (mod 4)**, so a = 1 and K = 3^ε. If ε = 0, then m ≤ 1 = K is the central case. If
ε = 1, then m ∈ {1, 2}. Here B = n − 1 = 6A − 1 is prime to 3 and must divide m(6 − m) ∈ {5, 8},
so n = 6 and no j > 3 exists.

**4 | n.** Now (n − 2)/2 is odd. The prime powers split as B = B₁B₂ and C = C₀C₁C₂ with
B₁C₀ | m, C₁ | K − m and B₂C₂ | 2K − m. Hence

    BC  |  m(K − m)(2K − m)  ≤  max over 0<m<K  =  (2/(3√3))·K³.

At most one of n − 1 and n − 2 is divisible by 3, so BC ≥ (n − 1)(n − 2)/6. Therefore
(n − 1)(n − 2) ≤ (4/√3)·K³ with n = 2KA. ∎

## Consequences

- **Unconditional.** The i = 3 slice of P699 holds for every odd n and every n ≡ 2 (mod 4).
- **Verified far beyond brute force.** Every pair passing (*) for all odd primes of C(n,3)
  lives on a *special* n: one with 4 | n and the size bound. Up to 10¹⁸ there are 2,061,213
  special n. For each one, `structured.py` enumerates the candidates m by the Chinese remainder
  theorem over the splits of B. No pair with j > 3 passes. The only passes are the trivial j = 1
  at n = 2^a and n = 3·2^a. So **the i = 3 slice holds for every n ≤ 10¹⁸**. The atlas's
  exhaustive all-i sweep stops at 10⁸.
- **What remains for i = 3:** special n > 10¹⁸. These are n = 2^a·3^ε·A with odd part
  A ≲ 0.66·n^(1/3), which are sparse (about n^(1/3) of them up to n).
- **A heuristic, not a proof.** For a special n, each CRT candidate lands in [1, K) with chance
  about K/(BC) ≈ 1.5/(K·A²). There are at most 2^ω(B)·3^ω(C) candidates. Summed over all special
  n, the expected number of nontrivial passes converges. Nothing in this note turns that into a
  proof.

## Transferable idea (for the substrate)

*Keep the position.* When q ≥ i is a prime with q^e ‖ n − t and q ∤ C(n,j), q^e divides j − r
for some r ≤ t. It is not just some factor of the falling factorial.
- For i = 3 this turns a size argument that failed into a divisibility structure,
  BC | m(K − m)(2K − m). The small-n control below shows the difference.
- For i ≥ 4 the same bookkeeping applies to primes ≥ i. This is untried here.

## Replay

```sh
python3 -I experiments/claude-699-i3-position-20260928/check_small.py        # ~2 s
python3 -I experiments/claude-699-i3-position-20260928/structured.py         # to 1e12, ~4 s
python3 -I experiments/claude-699-i3-position-20260928/structured.py 1e15    # ~75 s, 206,665 special n
python3 -I experiments/claude-699-i3-position-20260928/structured.py 1e18 --jobs=3   # ~13 min
```

`check_small.py` checks three things:
1. (*) on every odd prime of C(n,3) that does not divide C(n,j), straight from the binomial
   coefficients, for all 87,912 pairs with 8 ≤ n < 600.
2. That no pair with n ≤ 3000 passes (*) for all odd primes.
3. A **negative control**: the position-blind condition does admit (10,5), (16,7) and (65,15),
   and (*) rejects all three.

`structured.py` does two things:
1. It first proves its CRT enumeration equals direct enumeration of every m on all special
   n ≤ 2·10⁵.
2. It then searches up to the given bound. It exits nonzero on any pass with j > 3.

The size bound is tested in exact integers, as 3L² ≤ 16K⁶.

| file | role |
|---|---|
| `position.py` | the condition (*), the position-blind condition, and the reduction's shape test |
| `check_small.py` | exact small-n checks and the negative control |
| `structured.py` | the special-n CRT search, with its own validation |
