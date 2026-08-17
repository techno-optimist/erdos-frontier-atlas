# q=6 all-maximizer three-row torsion wall (Erdős #142)

**Finite quotient census fence only.** No new `r_3(N)` bound, no continuum
certificate, and Problem 142 remains open.

## Claim

On the EHPS tile specialized at `q=6` (`epsilon=1/6`), enumerate all
`8^5 = 32,768` D4 role assignments on `(P1,P2,P3,B,K)`. Exactly **256** attain
the maximum five-cylinder union mass

```text
max union mass = 3,645 = 5 * 9^3
```

(the five Karapetyan cylinders are pairwise full products of 9-point role
supports). For **every** one of these 256 maximizers there exists at least one
ordered word-cylinder pattern `(w_x, w_y, w_z) ∈ {0..4}^3` and three full
cylinder vertices `X,Y,Z` such that

```text
 (X,Y,Z), (Y,X,Z), (X,Z,Y)
```

are modular midpoint witnesses with raw canonical squared endpoint costs
summing to a **strictly positive** integer. The three potential rows

```text
 +F(X) - 2F(Y) + F(Z)  ≥  c_XY / q²-scale
 -2F(X) + F(Y) + F(Z)  ≥  …
 +F(X) + F(Y) - 2F(Z)  ≥  …
```

cancel identically on the left while the right-hand sides sum positive.
Hence **no real-valued potential on the five-cylinder union** (even with
independent values at every full cylinder vertex) can satisfy all modular-
midpoint coercivity inequalities for that assignment.

## Coverage stratification (exact)

| screen | covered / 256 |
|---|---:|
| W2/W3 incidence template (`P2 ∩ P3 ≠ ∅`) | **128** |
| D4 orbit of `(0,1,0,1,0)` alone | **8** |
| W2/W3 ∪ orbit(01010) | **136** |
| **all 125 ordered word patterns** | **256** |

So the residual after the named W2/W3 + 01010 families is **120** maximizers,
but they are **not** open under the full three-row template screen: each admits
some (possibly cross-cylinder) pattern.

## Files

| file | role |
|---|---|
| `certificate.json` | compact census + named 01010 witness packet |
| `verify.py` | independent stdlib exhaustive verifier |
| `result_parent_sha256.txt` | sha of full parent `result.json` from discovery replay |

Expected independent verdict:

```text
PASS_Q6_ALL_MAXIMIZER_THREE_ROW_TORSION_WALL
```

Replay:

```bash
python3 -I verify.py --self-test
```

## Parent discovery

- Luna exhaustive screen: `D:/p42_research/erdos142_five_role_qp_20260817/luna_q6_all_torsion_templates_20260817/`
- Parent `result.json` sha256: `d21646888ae11c6c26f360d86b44079395f7f76c8bc83a6d33dcc54d581461cd`
- Packaged body sha256: `46b1e7ede89850760ce2ba7a3b04291c416c968747df52433f3fcfd163a0f4b4`
- Tick: `20260817T200620Z`

## Scope boundary

Finite `q=6` only. Does **not**:

- continuum-certify or take `q→∞` limits,
- improve any verified `r_3(N)` lower bound,
- kill recursive / finite-state / jointly deformed supports,
- replace the infinite `q=3m` W2/W3 family theorem (that remains a separate cert),
- close Wall A or mark `erdos142_solved`.

`continuum_certificate: false`. `erdos142_solved: false`. `new_r3_bound: false`.
