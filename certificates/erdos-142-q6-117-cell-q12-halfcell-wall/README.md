# Half-residual context-tile wall for the q=6 117-cell alphabet

## Result

Let \(U\) be the fixed 117-cell four-dimensional q=6 alphabet

\[
U=\{(a,b,a+d_1,b+d_2)\pmod 6:(a,b)\in S_0,\ d\in D\}.
\]

Split every residual coordinate of every q=6 cell into its lower and upper
half.  The resulting physical pieces are 1,872 distinct half-open q=12
microboxes.

For any horizon \(m\), let \(L_m\) be an arbitrary set of q=12 microbox words
drawn from these 1,872 boxes, and let \(P_m\) be the disjoint union of the
corresponding physical product boxes.  Assume a bounded, single-valued
physical function \(F_m:P_m\to\mathbb R\) satisfies, pointwise, every actual
raw-canonical torus midpoint inequality

\[
F_m(x)+F_m(z)-2F_m(y)\ \geq\ \lVert x-z\rVert_2^2
\quad\text{when }x+z\equiv2y\pmod1.
\]

Then

\[
|L_m|\leq1763^m
\]

and hence

\[
\mu(P_m)\leq(1763/20736)^m
          <(1764/20736)^m
          =(49/576)^m.
\]

Equivalently, measured in original q=6 cell units, the decoded exponential
rate is at most

\[
1763/16=110+3/16 < 441/4.
\]

Thus no finite-state or edge-owned construction made from complete
half-residual microboxes of the fixed 117 cells can clear the EHPS
four-coordinate gate while retaining such a physical potential.  This
includes arbitrary state lifts, arbitrary memory, horizon-dependent path
languages, unions of multiple microboxes on an edge, and overlaps between
different abstract paths.  Repeated abstract decodings count only once.

## Exact 109-edge quotient

For a coarse q=6 digit vector \(c\) and residual-half word
\(\beta\in\{0,1\}^4\), the physical q=12 digit vector is

\[
d=2c+\beta.
\]

If \(c\) has coarse-cell index \(i\), the verifier's scalar microbox label is
\(16i+\operatorname{bin}(\beta)\), with the four-bit words in lexicographic
order.
Orient \(A\to B\) when every scalar digit is equal or decreases by one modulo
12 and at least one coordinate is a genuine \(0\to11\) wrap.  Exact
enumeration gives 676 oriented edges.

The 21 disjoint q=6 dilation pairs from the coarse certificate lift to 106
disjoint q=12 edges.  Three further disjoint edges are

\[
(0,195),\qquad(4,199),\qquad(656,627).
\]

In physical q=12 digits these are

\[
\begin{aligned}
(6,4,6,0)&\to(6,4,5,11),\\
(6,5,6,0)&\to(6,5,5,11),\\
(8,2,10,0)&\to(8,2,9,11).
\end{aligned}
\]

The resulting matching has 109 edges.  Merging the endpoints of each edge
and leaving every other microbox as a singleton gives

\[
1872-109=1763
\]

quotient classes.

## Pointwise word telescope

For a scalar q=12 digit \(a\), let \(b=a-1\pmod {12}\).  On an oriented
matching edge, use residuals

\[
A(t)=(a+t)/12,\qquad B(t)=(b+1-t)/12.
\]

For \(0<t<1/3\), all residuals \(t,3t,1-t,1-3t\) are strict interior points.
The two actual torus midpoint rows are

\[
(A(t),B(t),B(3t)),\qquad(A(3t),A(t),B(t)).
\]

Write

\[
F_m(x)=2\lVert x\rVert_2^2+h_m(x)/12^2.
\]

For an ordinary predecessor coordinate both scaled correction costs are zero.
For a \(0\to11\) wrap they are exactly

\[
432-48t,\qquad -144-48t,
\]

whose sum is \(288-96t>0\).

Suppose two distinct accepted microbox words have the same quotient word.
At every differing block orient their matching pair independently and use the
same parameter \(t\); equal coordinates use fixed residual \(1/2\).  This
constructs four actual points \(X(t),X(3t),Y(t),Y(3t)\) inside \(P_m\).
Adding the two whole-word midpoint inequalities cancels the arbitrary global
values in the exact combination

\[
D(3t)-D(t),\qquad D(t)=h_m(X(t))+h_m(Y(t)).
\]

Every matching edge has exactly one wrap, so if the words differ in \(K\geq1\)
blocks,

\[
D(3t)-D(t)\geq K(288-96t).
\]

At \(t_j=(1/4)3^{-j}\), summing \(j=1,\ldots,N\) gives the finite identity

\[
D(1/4)-D((1/4)3^{-N})
\geq K\left[288N-12(1-3^{-N})\right].
\]

The right side is unbounded in \(N\), contradicting boundedness of \(h_m\).
No limit, continuity, additivity, finite-dimensional potential ansatz, or
uniform-in-\(m\) bound is used.  Therefore the quotient map is injective on
\(L_m\), proving the word-count bound.

## Finite-state and physical-volume interpretation

Give each directed state edge any union of the 1,872 complete half-residual
microboxes and form path products.  Expanding every edge union produces a
language of microbox words.  Different state paths may decode to the same
word; the physical union contains that half-open word box once.  After this
deduplication the preceding theorem applies to the decoded language without
any regularity or finite-state assumption.

Consequently:

- if decoding is injective, the weighted path/Perron rate itself is at most
  1,763 in q=12 microbox units;
- if decoding overlaps, the abstract weighted Perron rate may be larger, but
  it is not physical volume; the distinct decoded-word rate is still at most
  1,763.

This is why state multiplicity cannot manufacture the missing mass.

## Exact scope

The result closes:

- the fixed q=6 117-cell geometry split into all coordinatewise residual
  halves;
- any union of those complete half-open q=12 microboxes on a state or edge;
- arbitrary decoded word languages, including non-Markov and
  horizon-dependent ones;
- arbitrary bounded, fully coupled, residual-dependent physical potentials;
- arbitrary abstract path overlap, after exact physical deduplication.

It does **not** close:

- proper measurable pieces inside a q=12 microbox;
- a finer residual partition;
- non-axis-aligned carving or deformation;
- tiles coupled across multiple consecutive four-dimensional blocks that do
  not expand as unions of q=12 word boxes;
- almost-everywhere rather than pointwise coercivity;
- wrapped/geodesic endpoint cost, unbounded corrections, or integer transfer.

So this is a rigorous first residual-resolution wall, not a solution of
Erdos Problem 142.

## Replay

Run:

    python -I verify_halfcell_context_wall.py --self-test

The verifier uses only the Python standard library.  It reconstructs the
coarse and refined alphabets, enumerates and hashes all 676 dilation edges,
rebuilds the 109-edge matching, checks every scalar raw-canonical row and a
mixed-orientation global word row, verifies the finite telescope and exact
density comparison, explicitly deduplicates overlapping abstract paths, and
rejects planted corruptions.
