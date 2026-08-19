# Independent full-word strict-dilation quotient audit

## Verdict

**PASS.**  Seven disjoint strict-dilation pairs already force every complete-
box word language carrying an arbitrary bounded residual-dependent correction
below the four-dimensional EHPS gate.  A complete independent census gives an
optional strengthening from seven pairs to a maximum matching of 21 pairs.

The theorem is not a label-table cancellation.  It uses actual strict-interior
points at successively smaller residual scales and a finite telescope, so the
correction may be an arbitrary bounded nonseparable function of all `4m`
physical coordinates.

## 1. Exact componentwise dilation graph

Let `U` be the fixed 117 q=6 four-dimensional cells.  An ordered pair `(A,B)`
is a componentwise strict-dilation pair when, in every scalar coordinate,

```text
B_i=A_i, or B_i=A_i-1 (mod 6),
```

and at least one active coordinate is a genuine canonical wrap
`A_i=0,B_i=5`.  At an unchanged coordinate use one fixed strict residual.  At
an active coordinate and `0<t<1/3`, use

```text
P_A(t)=t,       P_A(3t)=3t,
Q_B(t)=1-t,     Q_B(3t)=1-3t.
```

The two forward word orientations are the actual rows

```text
(P_A(t), Q_B(t), Q_B(3t)),
(P_A(3t), P_A(t), Q_B(t)).
```

At a nonwrap active coordinate both carries and correction requirements are
zero.  At a wrapped coordinate their carries are `-1,+1` and their exact
`q^2=36`-scaled correction requirements are

```text
R1(t)=108-24t,
R2(t)=-36-24t,
R1(t)+R2(t)=72-48t > 0.
```

For the reverse word orientation, interchange A and B and swap the endpoint
order.  The first row then has cost R2 and the second has cost R1, so the same
strict positive sum results.  No half-open closure limit is used.

Independent enumeration gives exactly 66 ordered pairs.  The active-coordinate
histogram is `1:11, 2:38, 3:10, 4:7`; the wrap-coordinate histogram is
`1:61, 2:5`.

## 2. The sufficient seven-pair quotient

The proposed simple pairs are

```text
(25,24), (37,36), (41,40), (47,46),
(77,76), (79,78), (84,86).
```

Their 14 endpoints are distinct.  Every pair differs in exactly one
coordinate, which is a wrapped `0 -> 5` coordinate, so each has the exact
strict cost sum `72-48t` in both word orientations.

Merge the endpoints of each pair and leave all other labels singleton.  The
quotient alphabet therefore has

```text
7 + (117-14) = 110
```

classes.  Six pair merges would leave 111 classes, so seven is the smallest
number of disjoint doubleton identifications whose raw class count falls
strictly below `441/4=110.25`.

## 3. Optional exact maximum matching

Treat the 66 ordered pairs as undirected edges for endpoint-disjointness.  The
following 21 directed edges are pairwise vertex-disjoint and belong to the
exact census:

```text
(55,3), (17,4), (59,12), (68,16), (25,24), (37,36), (52,39),
(53,40), (105,41), (96,46), (106,54), (69,56), (111,64),
(77,76), (79,78), (93,80), (84,83), (87,86), (92,91),
(99,98), (104,116).
```

It is maximum.  The undirected dilation graph has components of sizes 40, 4,
and 73 isolated vertices.  Remove the two vertices

```text
S={12,46}.
```

The remaining graph has components of sizes 35, 4, and 76 singletons.  Hence
it has 77 odd components.  In any matching, at most the two vertices of S can
match vertices from two of those odd components outward; at least

```text
77-|S| = 75
```

vertices remain unmatched.  Thus every matching has at most
`(117-75)/2=21` edges, and the displayed matching attains the bound.  Merging
it gives 96 quotient classes.

## 4. Global full-word telescope

Fix a horizon of `m` physical four-dimensional blocks and a language

```text
L_m subset U^m
```

whose physical set is the disjoint union of the complete q-cell product boxes
indexed by its distinct words.  Let

```text
F_m(x)=2||x||_2^2 + H_m(x)/36,
```

where `H_m` is any bounded finite real-valued function on that physical union.
It may be measurable, discontinuous, residual-dependent, nonadditive,
position-dependent, and nonseparable across blocks.

Let `kappa` merge the endpoints of either the seven-pair or 21-pair matching.
Suppose two distinct accepted words `Aword,Bword` have the same coordinatewise
quotient word.  At equal blocks choose one common strict-interior point.  At a
differing block use the componentwise construction above, with orientation
chosen according to which word contains the directed A endpoint.  Using one
common `0<t<1/3` for every active scalar coordinate gives two actual global
torus-midpoint rows

```text
(P(t), Q(t), Q(3t)),
(P(3t), P(t), Q(t)),
```

where `P(t),P(3t)` lie in the complete box of `Aword` and `Q(t),Q(3t)` lie in
the complete box of `Bword`.  Crucially, no hybrid word is introduced.

Let `W>=1` be the total number of wrapped scalar coordinates among all
differing blocks.  Nonwrap active coordinates contribute zero.  The two
required inequalities add to

```text
D(3t)-D(t) >= W(72-48t),
D(t)=H_m(P(t))+H_m(Q(t)).                (1)
```

This identity is valid even if many blocks differ and their directed
orientations are mixed: reversing a block only swaps whether R1 or R2 appears
in the first global row, while their sum is unchanged.

If `|H_m|<=M`, take `T=1/4`, `t_n=T/3^n`, and sum (1) for `n=1,...,N`:

```text
D(T)-D(T/3^N)
  >= 72WN - 6W(1-3^-N).                 (2)
```

The left side is at most `4M`.  For example,

```text
N=floor((4M+6W)/(72W))+1
```

makes the right side strictly greater than `4M`.  This is a finite
contradiction involving only strict-interior points.  It uses no continuity,
closure, affinity, additivity, or uniform bound as `m` varies.

Therefore `kappa^m` is injective on `L_m`.

## 5. Exact word and density bounds

The seven-pair quotient gives, at every horizon,

```text
|L_m| <= 110^m < (441/4)^m.
```

Since every complete word box has measure `1296^-m`, this is strictly below
the EHPS four-dimensional product gate.  The maximum matching strengthens the
count to

```text
|L_m| <= 96^m.
```

The bound concerns distinct physical word boxes.  Repeated automaton
representations do not create additional volume.

## Scope fence

The theorem applies to complete product boxes from the fixed 117-cell
alphabet and one bounded, single-valued physical correction `H_m` on their
union.  It is independent of how a decoder or automaton presents the language.
It does not cover proper measurable carving inside word boxes, overlapping
context-owned subtiles counted with controlled multiplicity, unbounded
corrections, deformed cells, weighted/repeated physical pieces, integer
transfer, a new `r_3(N)` bound, or a solution of Problem 142.
