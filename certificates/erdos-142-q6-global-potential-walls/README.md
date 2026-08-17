# q=6 arbitrary global-potential walls (Erdos #142)

**A finite-quotient wall, not a new bound.** These certificates do not give
a new `r_3(N)` lower bound, certify a continuum construction, or solve
Problem 142.

## Claim

Specialize the EHPS tile to `q=6`, `epsilon=1/6`, form the five Karapetyan
product cylinders, and use either D4 role assignment

```text
A = (P1,P2,P3,B,K) = (7,7,7,6,7),
B = (P1,P2,P3,B,K) = (7,6,7,6,7).
```

Each local support has nine points. For both assignments the five cylinders
are pairwise disjoint, so the union has exactly

```text
5 * 9^3 = 3,645
```

vertices. Its normalized mass is `3645/6^6 = 5/64`, and it exceeds the
finite EHPS comparison mass by the exact ratio

```text
(5/64) / (7/24)^3 = 1080/343 > 1.
```

Now give every one of the 3,645 union vertices an independent real potential
value. This is the unrestricted global potential on the finite union: there
is no additive, pair-coordinate, cylinder-position, polynomial, or other
factorization assumption. Across all 125 ordered cylinder triples there are
exactly 1,128,545 actual modular-midpoint witnesses, including every even-`q`
midpoint branch.

Neither A nor B admits a potential satisfying all raw-canonical Euclidean
coercivity rows. Exact positive Farkas combinations prove this:

| representative | selected rows | exact contradiction numerator |
|---|---:|---:|
| A `(7,7,7,6,7)` | 3 | 48 |
| B `(7,6,7,6,7)` | 646 | `1008002222684440065050502628243220937672543380399299618341618732116823199710099674644575626053135803548777716691742511099721130065976` |

For A, the entire obstruction is the transparent three-row cycle

```text
 +F(1948) - 2F(2673) + F(2681) >= 20
 -2F(1948) + F(2673) + F(2681) >= 20
 +F(1948) + F(2673) - 2F(2681) >=  8
```

whose left sides cancel and whose right sides sum to 48. The labels denote
the three union vertices reconstructed by both verifiers; the packet also
records their cylinder words, local points, midpoint branches, carries, and
raw endpoint costs. Thus the sum is the impossible inequality `0 >= 48`.
Dividing by `q^2=36` gives the equivalent normalized contradiction.

The B packet is a 646-row primitive positive integer ray. Its much larger
integer is only the exact scale of that ray; positivity and exact cancellation,
not its magnitude, are what matter.

## Exact replays

| file | role |
|---|---|
| `certificate_A.json` | semantic three-row Farkas packet for A |
| `certificate_B.json` | semantic 646-row Farkas packet for B |
| `verify.py` | primary stdlib semantic verifier and 18 planted corruptions |
| `independent_replay.py` | separately written stdlib reconstruction of both full finite models |
| `cycle_orbit_audit.py` | exact 8^5 assignment census and scope audit for A's tiny cycle |

Packet SHA-256 values after repository normalization:

```text
certificate_A.json  4e9fe8e052ee87e519a9d191e3ac46052f032bc7fe474cdd3e3b6d9b903515ef
certificate_B.json  dc865a45d6281b9640402ae341cb65b5d55b3eac82ae9f994687c59b81b1240f
```

Replay with:

```bash
python3 -I verify.py --self-test
python3 -I independent_replay.py --self-test
python3 -I cycle_orbit_audit.py
```

The primary verifier reconstructs the EHPS support, all eight D4 images, the
3,645 stable vertex labels, pairwise cylinder disjointness, exact mass gate,
the complete 1,128,545-witness count, every selected semantic row, and exact
integer cancellation. Its self-test rejects 18 planted corruptions. The
independent replay imports no primary or discovery module and explicitly
rechecks the three-row cycle.

## Scope boundary

This excludes exactly the two named `q=6` support assignments. It does not
transfer to `q=24`, `q=48`, a continuum tile, recursive or finite-state
potentials, jointly deformed supports, or an integer construction.

The exact assignment audit finds 256 maximum-mass D4 assignments at `q=6`.
Global D4 transports of A's particular three-row cycle hit 32 of them; 224
are untouched by that tiny-cycle screen. B is certified by its separate
646-row ray. No global impossibility claim is made for the other assignments.

`erdos142_solved: false`. `new_r3_bound: false`.

## Discovery provenance

- Fresh Terra CEGAR and exact rays:
  `D:/p42_research/erdos142_five_role_qp_20260817/terra_global_q6_exact_20260817/`
- Independent Luna replay:
  `D:/p42_research/erdos142_five_role_qp_20260817/luna_global_q6_exact_audit_20260817/`
- Luna exact cycle-scope census:
  `D:/p42_research/erdos142_five_role_qp_20260817/luna_q6_global_cycle_sweep/`
