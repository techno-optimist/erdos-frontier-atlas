# Degree-[3,7] family probe (dim-3 Keller counterexamples)

Date: 2026-07-20

## Quantity

`jc-min-counterexample-degree-dim3`: minimal max-component degree of a dim-3
Keller counterexample, bracket **[3, 7]** (Wang floor 3; Alpöge map degree 7).

## Family scanned

Alpöge-shaped maps with parameters \((k,a,b,c,d,e,f,g)\):

```
u = 1+xy
f1 = u^k z + y² u (a + b xy)
f2 = y + c x u^{k-1} z + d x y² (a + b xy)
f3 = e x + f x² y + g x³ z
```

Alpöge instance: \((3,4,3,3,3,2,-3,-1)\), degree 7, det ≡ −2.

### k=2 integer box

All coefficients in \(\{-2,\ldots,2\}\): **78 125** maps screened.

- Constant nonzero Jacobian and max degree ∈ {3,4,5,6}: **0 maps**
- Collision hits: **0**

Artifact: `CONST_JAC_K2.json` (`probe_const_jac_family.py`).

## Scope

Absence of hits is a **family fence**, not a proof that no degree-6
counterexample exists outside this shape (or with larger coefficients).
The constant-Jacobian constraint is extremely rigid already at \(k=2\).

## Replay

```sh
python3 -I probe_const_jac_family.py
```
