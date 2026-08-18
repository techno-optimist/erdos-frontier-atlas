# Independent hostile audit: q=12 half-cell wall

Verdict: **APPROVE, with a stronger solver-free matching.**

The replay at `independent_q12_halfcell_wall.py` was written without importing
the sibling packet or Atlas implementation.  It reconstructs the physical
alphabet from the nine base pairs and thirteen offsets and obtains exactly
1,872 distinct half-open q=12 boxes.  The numeric decoder is

```text
microbox_id = 16 * coarse_cell_index + lexicographic_four_bit_code,
physical_digit_vector = 2 * coarse_digit_vector + bit_vector.
```

The sibling README now states this distinction explicitly; its former numeric
ID ambiguity is resolved.

## Exact graph and matchings

Enumerating all nonempty predecessor masks gives exactly 676 oriented edges.
Every edge has at least one genuine `0 -> 11` wrap, and no reverse oriented
edge occurs.  Canonical edge-list SHA-256:

```text
fe25fe2b765bef0f573ad96997e2fe007fa99e81726caf7bf34ace943e895434
```

The claimed construction independently rebuilds as follows.  If a coarse
matching edge has `k` active coordinates, fixing active fine bits to `A=0`,
`B=1` and matching equal bits on inactive coordinates gives `2^(4-k)`
disjoint fine edges.  Summing over the 21 public coarse pairs gives 106.  The
three extra edges `(0,195)`, `(4,199)`, `(656,627)` are genuine, disjoint and
avoid all 106 endpoints.  Hence the claimed matching has 109 edges and gives
the valid quotient `1872-109=1763<1764`.

The replay also scans the same exact edge list lexicographically, accepting an
edge iff neither endpoint has appeared.  This deterministic solver-free rule
finds **148** disjoint edges, giving the stronger quotient

```text
1872 - 148 = 1724 < 1764.
```

Of these edges 147 have one wrap and one has two wraps; none has zero.  The
canonical greedy-matching SHA-256 is

```text
e49c28c5dd8e750ee1bfe71579e13d5dc38ef36545e7fc94424c3fee7cb7f521
```

No maximality claim is needed.  A separate discovery check found a matching
of size 154, but that solver result is deliberately absent from the theorem
and replay.

## Physical and analytic audit

For every scalar digit `a` and predecessor `b=a-1 mod 12`, exact polynomial
arithmetic checks both strict-interior rows and both endpoint orientations.
Ordinary predecessor coordinates contribute zero; a wrap contributes

```text
432 - 48 t,  -144 - 48 t,
```

so a pair of distinct quotient-colliding words gives

```text
D(3t)-D(t) >= K(288-96t),  K>=1.
```

At `t=(1/4)3^-j`, the finite sum is exactly

```text
D(1/4)-D((1/4)3^-N)
  >= K[288N-12(1-3^-N)],
```

contradicting boundedness.  A mixed 17-block replay alternates which accepted
word owns the oriented source box, preventing a one-orientation shortcut.

The physical decoder is injective at the box level: distinct q=12 digit words
are disjoint half-open product boxes.  Repeated abstract state paths decoding
to one word therefore count once.  The theorem concerns the decoded language,
not the possibly inflated abstract path partition function.

## Planted controls and scope

The replay rejects a wrap-free ordinary predecessor, an endpoint-reusing
matching mutation, and a noninjective physical decoder mutation.  It freezes
the edge and both matching digests and checks native Windows and WSL outputs.

This closes arbitrary languages of complete q=12 half-microboxes and arbitrary
bounded, fully coupled pointwise physical potentials.  It does not close
proper pieces inside a half-microbox, finer/non-axis-aligned carving,
multi-block tiles that do not expand into q=12 words, almost-everywhere-only
coercivity, unbounded corrections, or integer transfer.

## Commands and artifact hash

```powershell
python -I D:\p42_scratch\erdos142_context_subtiles\independent_q12_halfcell_wall.py
wsl.exe python3 -I /mnt/d/p42_scratch/erdos142_context_subtiles/independent_q12_halfcell_wall.py
```

Final replay SHA-256:

```text
d86f7a7e385dda7db108cd17dfb52cc16314a77350ff280eb4dd95e27d3c0732
```
