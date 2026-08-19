# At-most-fourteen-state homogeneous partial-decoder wall

Date: 2026-08-19. This is a scratch-only structural theorem package. It
changes no Atlas or pull-request byte. It replaces the proposed seven-state
orbit census by an exact proof and, without additional enumeration, extends
the same wall through fourteen live states.

## Frozen coloring and interface

Use the already frozen support-disjoint q42 packet packing and choose exactly
one red box in each of its 17,640 packets. Every other q42 box is blue. Thus

```text
R = 17640 = 441*40,
B = 263277 = 441*597,
G = 1058841/4,
B < G.
```

A color-homogeneous partial deterministic interface has at most one blue and
one red successor at each state. On a strong live component write

```text
W = B A + R C,
```

where `A` and `C` are the zero-one matrices of the partial blue and red maps.
Rows are sources and columns are targets. A nondegenerate
seven-multisunflower is a multiset of seven accepted words of one common
length whose column red counts lie in `{0,1,7}`, with at least one unit-red
column. Repeated words are allowed, exactly as in the frozen six-state
histogram product.

## Theorem

**Theorem.** Let `W` be a strong color-homogeneous partial deterministic
table on `m` states.

1. If its blue map is acyclic and `m <= 14`, then `rho(W) < B`.
2. If its blue map contains a directed cycle, then either the table is the
   blue-only spanning directed cycle and `rho(W)=B`, or `rho(W)>B` and the
   seven-copy product has a nondegenerate pure-to-pure witness for every
   ordered start/target pair.

Consequently, if a color-homogeneous partial deterministic interface with at
most fourteen live states contains no nondegenerate seven-multisunflower,
then its accepted-language/live-trim rate satisfies

```text
lambda <= B = 263277 < G.
```

The rate bound is sharp at a blue-only recurrent cycle.

## Acyclic-blue proof: an explicit integer Collatz vector

Assume the partial blue map is acyclic. Every blue trajectory becomes
undefined in at most `m` steps. Define

```text
v = (I + A + A^2 + ... + A^(m-1)) 1.
```

Equivalently, `v_s` is the number of states in the blue tail beginning at
`s`. Hence

```text
1 <= v_s <= m,
A v = v - 1,
C v <= m 1.
```

All quantities are integers. Therefore

```text
W v = B A v + R C v
    <= B v - (B-mR) 1.
```

For `m<=14`,

```text
B-mR >= B-14R = 16317 > 0.
```

Thus `Wv < Bv` coordinatewise. The strict Collatz bound gives `rho(W)<B`.
No determinant, floating point calculation, enumeration, or irreducibility
is needed in this branch.

## Cyclic-blue proof: an explicit exceptional word

Let

```text
x ->blue ... ->blue x
```

be a blue cycle of length `k`. The embedded weighted cycle has Perron root
`B`. Since `W` is irreducible and dominates it, strict Perron monotonicity
gives `rho(W)>B` unless `W` is exactly that cycle. Exact equality can therefore
occur only when the cycle spans all `m` states and every red transition is
undefined.

Now exclude that equality table. There is a red edge from some blue-cycle
vertex `x`:

- if the blue cycle is proper, the first edge of a path leaving it must be
  red, because every blue edge on the cycle stays on the cycle;
- if the cycle spans all states, a nontrivial table has a defined red edge.

Write that edge as `x ->red y`. Strong connectivity supplies a word `p` from
`y` back to `x`, of length at most `m-1`. Then

```text
u = red p
```

is a closed word at `x`, contains a red letter, and has length at most `m`.
Set `w=u^k`. Its length is divisible by `k`, so both `w` and the all-blue word
of the same length send `x` to `x`.

Let one of seven copies follow `w` and let the other six follow blue at every
coordinate. At a blue letter of `w`, the column is all blue. At a red letter
of `w`, the column has one red copy and six blue copies. The latter blue
transitions are always defined because the six ordinary copies remain on the
blue cycle. The exceptional copy follows the defined word `w`. All seven
copies finish at `x`, and at least one column is unit-red.

This is an explicit active pure `x -> x` product loop. For arbitrary states
`s,t`, prepend one common word from `s` to `x` and append one common word from
`x` to `t`. Common columns have red count zero or seven and preserve the unit
column. Choosing shortest paths gives the uniform witness-horizon bound

```text
(m-1) + k*|u| + (m-1) <= m^2 + 2m - 2.
```

In particular, every seven-state witness has length at most 61. This proof
answers all 49 start/target pairs at once and does not inspect any of the
79,672,638 seven-state table orbits.

## Live-trim reduction and physical lift

For an arbitrary interface, delete unreachable and noncoaccessible states
and make transitions entering a deleted state undefined. The
accepted-language rate is the Perron root of this live trim. If it exceeds
`B`, choose a Perron SCC, one common prefix entering it, and one common suffix
from it to the accepting set. The SCC is a strong partial table on at most
fourteen states. The theorem gives a pure-to-pure multisunflower inside the
SCC; the common prefix and suffix lift it back to seven accepted words.

The physical q42 lift is unchanged from the frozen six-state package. At a
unit column, cyclically align the unique red word with the red role of the
explicit actual size-seven packet. At a common column, use one common
physical symbol. The existing packet-incidence cancellation and positive raw
cost apply verbatim; the structural proof changes only how the abstract word
witness is obtained.

## Exact cutoff of the acyclic argument

The universal state-count estimate is sharp for this Collatz method. On 15
states let blue be the chain

```text
0 -> 1 -> ... -> 14 -> undefined
```

and let every red edge return to zero. This table is strong and blue-acyclic.
For `P=(I-A)^(-1)`, the matrix `PC` has rank one and Perron root 15. Hence

```text
rho((R/B) P C) = 15*40/597 = 600/597 > 1,
```

which implies `rho(BA+RC)>B`. This is not claimed to be sunflower-free and is
not a counterexample to a fifteen-state wall. It only proves that the uniform
acyclic state-count estimate cannot be extended from 14 to 15.

The more precise reusable criterion is: if the blue map is acyclic and the
largest blue-tail potential among red targets is `h`, then `hR<B` implies
`rho(W)<B`. Thus the proof also covers larger interfaces with sufficiently
short blue tails.

## Exact replay

Run

```powershell
python .\verify_structural_closure.py
```

The verifier performs the following independent finite checks around the
proof:

1. exhausts every partial blue map through seven states, checks the tail
   vector identity, and recovers the rooted-forest count
   `(m+1)^(m-1)` for the acyclic maps;
2. exhausts every partial binary table through four states, recovers the
   known strong counts `4,25,828,60654`, classifies its Perron sign by all
   exact principal minors, and constructs and validates all cyclic-above
   pure-to-pure word witnesses;
3. checks the exact fourteen-state margin and the fifteen-state sharpness
   control.

The terminal marker is

```text
PASS_EXACT_Q42_HOMOGENEOUS_PARTIAL_STRUCTURAL_CLOSURE
```

## Scope and nonclaims

Proved: the frozen one-red-per-packed-packet q42 coloring;
color-homogeneous partial deterministic interfaces with at most fourteen live
states; accepted-language/live-trim rate; every ordered singleton target;
and the unchanged explicit physical packet lift.

Not proved: a wall for arbitrary fifteen-state interfaces; arbitrary
same-count colorings; physical-symbol-dependent transitions; box-sensitive
or state-carved transitions; nondeterministic ownership; unbounded-state
interfaces; a physical potential from packet avoidance; a new bound for
`r_3(N)`; or Erdős Problem 142 itself.
