# Erdős #552 exact small-value certificates

This directory certifies five red graphs proving

```text
R(C4,K1,n) = n + ceil(sqrt(n)) + 1,  12 <= n <= 16.
```

For each `n`, `witnesses.json` gives a graph on
`m = n + ceil(sqrt(n))` vertices. The verifier checks that every pair of
vertices has codegree at most one (so the graph is C4-free) and that every
vertex has degree at least `m-n` (so the blue complement has no K1,n). This
gives `R(C4,K1,n) >= m+1`. Parsons' published general upper bound
`R(C4,K1,n) <= n + ceil(sqrt(n)) + 1` supplies the matching inequality.

Run:

```sh
python3 certificates/erdos-552/verify.py
```

The graph check is dependency-free and exact. The verifier does not prove
Parsons' theorem; that theorem is the cited mathematical reduction. See
[Erdős Problems #552](https://www.erdosproblems.com/552), which attributes the
upper bound to Parsons (1975), and [OEIS A006672](https://oeis.org/A006672)
for the previously published terms through `n=11`.

The same certificate set also includes a 21-vertex witness for `n=17`, proving
`R(C4,K1,17) >= 22`.

**Closure (source-freshness correction, 2026-07-16).** The `n=17` cell is not
open:

```text
R(C4,K1,17) = 22.
```

The value has been known since Parsons (1975), whose theorem
`R(C4, K1,q^2+1) = q^2 + q + 2` applies at `q = 4`; Boza's 2026 survey table
(arXiv:2409.12770) lists `f(17) = 22` citing exactly that paper. It also
follows elementarily from published extremal numbers: a 22-vertex C4-free
graph of minimum degree 5 would need `ceil(22*5/2) = 55` edges, but
`ex(22; C4) = 52` ([OEIS A006855](https://oeis.org/A006855)), so no such graph
exists and `R(C4,K1,17) <= 22`. The certified 21-vertex witness supplies the
matching lower bound. The earlier bounded SAT run that returned `UNKNOWN` on
the 22-vertex cell was searching for a witness that provably cannot exist.

Per Boza (arXiv:2409.12770, Jun 2026), exact values of `R(C4,K1,n)` are now
known for **all** `n <= 38`; the first open cells are `n = 39` (`f <= 46`),
`n = 42` (`f <= 50`), and `n = 44` (`f <= 52`).
