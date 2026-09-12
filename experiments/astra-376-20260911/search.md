# Complete A030979 prefix through 3^35

**Not a solution of #376.** Infinitude remains open.

## Python (CI)

`search_base3(20)` is complete through \(3^{20}\) and matches OEIS through 59548401.
C D=12 (including split ranges) matches Python.

## C replay

```sh
clang -O3 -o /tmp/search_base3 experiments/astra-376-20260911/search_base3.c
# 8 shards of 2^35, ~195s wall
/tmp/search_base3 35 START END
```

| D | cutoff | wall | hits |
|---|---|---|---|
| 24 | \(3^{24}=2.82\times 10^{11}\) | 0.63s | 17 |
| 31 | \(3^{31}=6.18\times 10^{14}\) | 84.7s | 18 |
| 35 | \(3^{35}=5.003\times 10^{16}\) | 195s, 8-way | **43** |

The 43 hits are `hits-d35.txt`. They are exactly A030979(1..43) from the OEIS b-file. No extras below \(3^{35}\). Next b-file term \(673\,333\,777\,170\,421\,930\) exceeds this cutoff.

Among terms through \(3^{24}\), base-11 digits all ≤5 only at **0, 1, 3160**.
