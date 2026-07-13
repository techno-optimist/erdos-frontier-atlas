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

The next open cell in this snapshot is `n=17`, currently bracketed
`21 <= R(C4,K1,17) <= 23`. A bounded SAT run at the top endpoint returned
`UNKNOWN`; it is not a nonexistence result.
