# Strict-dilation wall for arbitrary full-cell word languages

## Theorem

Let `U` be the fixed 117-cell q=6 four-dimensional alphabet.  For any positive
integer `m`, let `L_m subset U^m` be an arbitrary decoded word language and let
`P_m` be the disjoint union of the complete q-cell product boxes indexed by
`L_m`.  Here `m` is the number of physical four-dimensional blocks, not an
automaton's transition count or hidden boundary-context length.  Repeated
abstract decodings count once, and

```text
mu(P_m)=|L_m|/1296^m.
```

Suppose a bounded function `F:P_m->R` satisfies, pointwise for every actual
raw-canonical modular midpoint triple in `P_m`,

```text
F(x)+F(z) >= 2F(y)+||x-z||_2^2.
```

Then

```text
|L_m| <= 96^m.                                      (T)
```

Thus no full-cell word language with a bounded, single-valued,
residual-dependent physical potential can reach the four-dimensional EHPS
numerator gate

```text
441/4 = 110.25.
```

The conclusion is per horizon and makes no Markov, finite-state, additive,
continuity, affinity or measurability assumption.  `F` may be nonadditive,
position-dependent and length-dependent.  No uniform bound in `m` is needed;
boundedness at the horizon under consideration suffices.  Consequently every
subexponential-range candidate in the full-box model is excluded.

## The 66-edge dilation graph and a 21-edge matching

Orient a pair of distinct cells `A->B` when, in every scalar coarse digit,

```text
B_i=A_i                  or                  B_i=A_i-1 mod 6,
```

and at least one coordinate makes the genuine wrap `A_i=0, B_i=5`.  Exact
enumeration gives 66 oriented pairs.  The primary replay verifies this
21-edge disjoint matching, shown below in its orientation-preserving order:

```text
(55,3),   (17,4),   (68,16),  (25,24),  (37,36),
(52,39),  (53,40),  (96,46),  (106,54), (59,12),
(69,56),  (77,76),  (79,78),  (84,83),  (87,86),
(92,91),  (93,80),  (99,98),  (105,41), (111,64),
(104,116).
```

Each edge in this matching has exactly one wrapped scalar coordinate; it may
also have ordinary decrement coordinates.  Merge the endpoints of the 21
pairs and leave the other 75 labels singleton.  This gives a quotient

```text
kappa: U -> {0,...,95}.
```

If `|L_m|>96^m`, distinct accepted words `A,B` have the same quotient word.
At every differing block their labels form one oriented matching edge, in one
of its two word orientations.

## Exact scalar rows

For one active coordinate, write its digit in the oriented first cell as `a`
and in the second as `b=a-1 mod 6`.  For `0<t<1/3`, use residuals `t,3t` in
the first cell and `1-t,1-3t` in the second.  The actual coordinates are

```text
A(t)=(a+t)/6,             A(3t)=(a+3t)/6,
B(1-t)=(b+1-t)/6,         B(1-3t)=(b+1-3t)/6.
```

Consider the two midpoint rows

```text
(A(t),  B(1-t), B(1-3t)),
(A(3t), A(t),   B(1-t)).
```

For an ordinary decrement `a>0`, both are Euclidean midpoint rows with carry
zero and correction cost zero.  For a wrap `a=0,b=5`, their carries are `-1`
and `+1`, and their exact `q^2`-scaled correction right sides are

```text
108-24t,                 -36-24t.                    (1)
```

Swapping the endpoint roles handles the reverse word orientation and reverses
the order of the two costs.  Every residual displayed above lies strictly in
`(0,1)`.  Equal coarse coordinates use residual `1/2` in all roles and cost
zero.  Therefore these are actual strict-interior physical triples, not
closure limits.

The replay checks (1) symbolically from

```text
36*((x-z)^2-2x^2-2z^2+4y^2),
```

the correction right side after writing

```text
F(x)=2||x||_2^2+h(x)/36.
```

## One simultaneous global recurrence

Let `A,B in L_m` be distinct words in one quotient fibre.  At every differing
coordinate assign residual `t` to the oriented first cell and `1-t` to the
second, independent of which word contains which cell.  Equal blocks remain
fixed.  This defines physical points `X(t)` in the box for word `A` and `Y(t)`
in the box for word `B`.

The two global midpoint triples are

```text
(X(t),  Y(t),  Y(3t)),
(X(3t), X(t),  Y(t)).                              (2)
```

Let `K` be the total number of wrapped scalar coordinates across all differing
blocks.  Every matching edge has a wrap, so `K>=1`.  Ordinary decrement
coordinates and equal coordinates contribute zero.  At each wrap, the two
rows in (2) contribute the two quantities in (1), in an orientation-dependent
order.

Define

```text
D(t)=h(X(t))+h(Y(t)).
```

Adding the two required global inequalities gives

```text
D(3t)-D(t) >= K*(72-48t),       0<t<1/3.             (3)
```

This uses one pair of simultaneous global rows.  It does not assume that `h`
splits across blocks, so arbitrary residual interactions and sliding-window
context dependence do not escape the recurrence.

## Finite boundedness contradiction

Fix `T=1/4` and apply (3) at `t=T/3^j`, `j=1,...,N`.  Telescoping gives

```text
D(T)-D(T/3^N)
  >= 72*K*N - 6*K*(1-3^-N).                          (4)
```

If `|h|<=M`, the left side is at most `4M`.  Taking

```text
N=floor((4M+6K)/(72K))+1
```

makes the right side strictly larger than `4M`, a contradiction.  Only
finitely many strict-interior points are used.

Thus the quotient map `kappa^m` is injective on `L_m`, proving (T).  In density
terms,

```text
mu(P_m) <= (96/1296)^m
          < ((441/4)/1296)^m
          = ((7/24)^2)^m.
```

## Replays

```powershell
python -I verify_dilation_word_wall.py --self-test
python -I verify_seven_pair_dilation_word_wall.py --self-test
```

The primary standard-library replay reconstructs the 117 cells and all 66
oriented dilation edges; verifies the 21-edge matching and 96-class quotient;
symbolically checks all six digit transitions, both word orientations and all
wrap/nonwrap costs; builds one 21-block mixed-orientation global row pair;
checks the exact finite telescope; and rejects matching, quotient and wrap
mutations.

The independently structured seven-pair replay uses only

```text
(25,24), (37,36), (41,40), (47,46),
(77,76), (79,78), (84,86).
```

These pairs differ in one 0/5 coordinate and give a 110-class quotient,
already sufficient because `110<441/4`.  It independently checks a
mixed-orientation nine-block construction and the same finite telescope.

## Relation to the word-constant control packet

The companion scratch packet
`erdos142_luna_117_sliding_window_quotient_wall_20260818` uses 27 ordinary bad
pairs to obtain `|L_m|<=90^m`, but only when the correction is constant on each
decoded word box.  The strict-dilation packet gives the numerically weaker but
still sufficient `96^m` bound while upgrading the functional scope to every
bounded residual-dependent physical potential on the unchanged full boxes.

## Scope fence and exact live frontier

The theorem requires every point of each accepted q-cell word box and requires
the coercivity inequality pointwise for every actual physical midpoint triple.
An abstract triple automaton may not discard a physical triple because chosen
hidden lifts fail to synchronize.  An almost-everywhere-only inequality is not
enough: the displayed dilation curves can be null.

The theorem does not cover context-owned proper subtiles, partial carving,
changed half-open ownership, deformed cells, or a physical path volume defined
by an overlap kernel instead of complete decoded word boxes.  Those changes
can delete the strict rows used in (2).  They must come with an exact
overlap-aware mass calculation, a single-valued bounded physical potential,
and a synchronized midpoint/wrap certificate.

Accordingly, the smallest remaining sliding-window model is a radius-2 or
radius-3 system of proper measurable context subtiles with a verified transfer
operator.  This packet does not construct such a model, perform an integer
transfer, improve the known `r_3(N)` exponent, or solve Erdős Problem 142.
