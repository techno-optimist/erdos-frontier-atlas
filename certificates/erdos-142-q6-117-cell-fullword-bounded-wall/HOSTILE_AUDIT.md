# Hostile audit: seven-pair full-word bounded wall

## Verdict

**APPROVE, with the stated physical scope.** The seven supplied oriented pairs
are disjoint q=6 cell pairs that differ in exactly one scalar digit, 0 versus
5. Merging them gives 110 quotient classes, and 110 < 441/4.

For any two accepted full-cell words in the same quotient fibre, let r be
their positive number of differing paired blocks. At each differing block, use
residual u in the 0 cell and 1-u in the 5 cell; use fixed strict interior
residuals on equal coordinates. Both word-level rows are strict modular
midpoints. In either orientation their direct raw-canonical
h=q^2(F-2||x||^2) right sides sum to:

~~~text
72 - 48t > 0,  for 0 < t < 1/3.
~~~

Adding all blocks and both rows gives, for arbitrary coupled physical h:

~~~text
D(3t)-D(t) >= r(72-48t),
D(u)=h(A(u))+h(B(u)).
~~~

At t_n=T/3^n, T=1/4, this telescopes exactly to:

~~~text
D(T)-D(T/3^N) >= r[72N-24T(1-3^-N)].
~~~

A bounded h makes the left side at most 4M, while a finite N makes the right
side larger. Thus same-quotient distinct words are impossible and
|L_m| <= 110^m. If a project indexes by transitions rather than word blocks,
replace m by m+1; the exponential base is still 110.

## Scope fence

This is exact only for a set of complete, disjoint-a.e. q-cell word products,
a single-valued bounded physical function, and the pointwise raw-canonical
modular-midpoint inequality for every eligible triple. It does not cover a
state-path multiset/weighted partition function, carved or coupled tiles,
graph-restricted triples, multivalued residual/state functions, an a.e.-only
condition, a geodesic/wrapped right side, or an unbounded correction.

## Replay

~~~powershell
python -I verify_seven_pair_fullword_bounded_wall.py
~~~

The replay is standalone and standard-library only. It checks both
orientations, direct raw-norm arithmetic, mixed multi-block tensors,
whole-word nonseparable correction cancellation, the finite telescope, gate
arithmetic, and planted residual/order/metric/matching/gate corruptions.
