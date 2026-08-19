# Two-level weighted multiset-7-sunflower bound

## Result and scope

This note strengthens the packet-screen-only weighted theorem for the frozen
q42 coloring.  It is a theorem about binary support families.  It does **not**
construct a physical potential, prove that packet avoidance is sufficient, or
give a new bound for `r_3(N)`.

Put

\[
x=\frac{R}{B}=\frac{40}{597},\qquad
y=\frac{G}{B}=\frac{2401}{2388}.
\]

A literally safe support family is an antichain with no seven distinct members
forming a nontrivial ordinary sunflower.  Tensor products of safe families are
safe and their weighted masses \(\sum_Sx^{|S|}\) multiply.  These facts are
replayed by the earlier frozen packet and are premises here.

The new result is a two-level uniform recursion.  It lowers the proved
rank-three cap from 744 to 672 and makes the exact LYM/cap relaxation exclude
the physical gate through dimension 33.  Dimension 34 is only the first
failure of this strengthened relaxation; it is not a construction.

## Sharp graph bases

Let \(A_k\) be an upper bound for the size of a \(k\)-uniform family with no
seven-sunflower.  Let \(B_k\) be the corresponding upper bound with matching
number at most five.  Every seven-sunflower-free family already has matching
number at most six.

The sharp graph bases are

\[
A_1=6,\quad B_1=5,\qquad A_2=42,\quad B_2=33.
\]

For graphs, a seven-sunflower is either a seven-edge star or a seven-edge
matching.  Thus the maximum degree is at most six.  The exact theorem of
Chvatal--Hanson, *Degrees and matchings*, J. Combin. Theory Ser. B 20 (1976),
128--138, gives for maximum degree \(\Delta=6\) and matching number \(\nu\)

\[
e\le 6\nu+3\left\lfloor\frac{\nu}{3}\right\rfloor.
\]

This is 42 for \(\nu=6\) and 33 for \(\nu=5\).  The bounds are attained by
\(2K_7\), and by \(K_7\mathbin\dot\cup K_{2,6}\), respectively.  The verifier
checks both witnesses and their exact maximum matching numbers without a
solver.

## Two-level link lemma

For \(k\ge3\), take a maximum matching \(M\) of size \(m\) in a safe
\(k\)-uniform family \(\mathcal F\), and put \(U=\bigcup M\),
\(W=V\setminus U\).  Write \(e_j\) for the number of members meeting \(U\)
in exactly \(j\) points.

For every \(u\in U\), its full link is a safe \((k-1)\)-uniform family with
matching number at most six, so it has at most \(A_{k-1}\) members.  Its link
restricted to \(W\) has matching number at most five: six disjoint restricted
link members, together with the matching petal \(E_u\setminus\{u\}\) from the
unique \(E_u\in M\) containing \(u\), would form a seven-sunflower with core
\(\{u\}\).  Hence the restricted link has at most \(B_{k-1}\) members.

Therefore

\[
e_1\le kmB_{k-1},\qquad
\sum_jj e_j\le kmA_{k-1}.
\]

The matching itself gives \(e_k\ge m\).  Since

\[
2|\mathcal F|
=e_1+\sum_jj e_j-\sum_{j\ge3}(j-2)e_j,
\]

we obtain

\[
2|\mathcal F|
\le m\left(k(A_{k-1}+B_{k-1})-(k-2)\right).
\]

Taking \(m\le6\), or \(m\le5\) in the restricted class, proves the coupled
recurrence

\[
\begin{aligned}
A_k&=3\left(k(A_{k-1}+B_{k-1})-(k-2)\right),\\
B_k&=\left\lfloor\frac52
\left(k(A_{k-1}+B_{k-1})-(k-2)\right)\right\rfloor.
\end{aligned}
\]

The first values are

\[
\begin{array}{c|rrrrrrr}
k&1&2&3&4&5&6&7\\ \hline
A_k&6&42&672&14778&406386&13410726&516312936\\
B_k&5&33&560&12315&338655&11175605&430260780.
\end{array}
\]

In particular \(A_3=672<744\).

## Exact weighted consequence

For a safe antichain \(\mathcal C\subseteq2^{[d]}\) not containing the empty
set, let \(n_k=|\mathcal C\cap\binom{[d]}k|\).  LYM and the new caps give

\[
\sum_k\frac{n_k}{\binom dk}\le1,
\qquad 0\le n_k\le\min\{\binom dk,A_k\}.
\]

The verifier solves the resulting fractional-knapsack relaxation with exact
`Fraction` arithmetic.  It proves

\[
U_d<1\quad(1\le d\le28),\qquad U_{29}>1,
\]

and, more importantly,

\[
U_d<y^d\quad(1\le d\le33),\qquad U_{34}>y^{34}.
\]

Thus the exact optimum remains one through dimension 28, and no literally safe
support family clears the q42 gate through dimension 33.  The inequalities at
29 and 34 go the wrong way only for the relaxation.  They do not exhibit a
safe family of mass above one or above the gate.

## Reproduction and nonclaims

Run `run.ps1`.  The trust path is Python standard library plus the cited sharp
graph theorem.  All recurrence and LP arithmetic is exact; graph lower
witnesses and maximum matchings are replayed directly.

This result does not resolve the unrestricted strong sunflower bound, does not
wall dimension 34, and does not prove an all-state automaton theorem.  It is a
support screen only: physical midpoint rows, a single-valued coercive
potential, continuum thickening, EHPS shelling, integer transfer, a new
`r_3(N)` bound, and Erdős Problem 142 all remain open.
