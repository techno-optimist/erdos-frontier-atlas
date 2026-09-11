# Complete A030979 prefix through 3^31

**Not a solution of #376.** Infinitude remains open.

## Python (CI)

`search_base3(20)` is complete through \(3^{20}\) and matches OEIS through 59548401.

## C replay (not CI)

```sh
clang -O3 -o /tmp/search_base3 experiments/astra-376-20260911/search_base3.c
/tmp/search_base3 31
```

D=24: 0.63s, 17 hits, cutoff \(3^{24}=282\,429\,536\,481\).
D=31: 84.68s real, 18 hits, cutoff \(3^{31}=617\,673\,396\,283\,947\).

Hits in order:

```
0, 1, 10, 756, 757, 3160, 3186, 3187, 3250,
7560, 7561, 7651, 20007, 59548377, 59548401,
45773612811, 45775397187,
237617431723407
```

Exactly the OEIS A030979 prefix through \(2.376\times 10^{14}\). No extras below \(3^{31}\). Next OEIS term \(24\,991\,943\,420\,078\,301\) is larger than this cutoff.

Among them, base-11 digits all ≤5 only at **0, 1, 3160**.
