# Exact horizon-two wall for the q=42 even-parity escape

## Result

The q=42 two-state even-parity language analyzed by the parent graph-wall
package cannot carry a single-valued global torus-coercive potential at horizon two,
for **any** choice of exactly one red vertex in each of the 17,640 packed
common-offset packets.

The obstruction is a seven-row physical Farkas cycle.  A literal-role
pigeonhole argument is enough to find it.  In fact the unique seven-point
packet has a transitive cyclic automorphism group, so any two of its 441 lifts
can be paired red-to-red even when their literal red roles differ.

This closes the particular parity escape as a potential construction.  It
does not invalidate its original, narrower use as an exact counterexample to
tensorizing one-block packet losses from full-context coordinate fibres.

## 1. Packet reconstruction and classification

The replay independently reconstructs the fixed 117-cell support, its
280,917 q=42 fine boxes, and the two disjoint packet layers from
`q42_fractional_carving_wall.py`:

```text
SHIFT1=(6,12): 30 usable prototypes x 441 lifts = 13,230 packets
SHIFT2=(0,6): 10 surviving prototypes x 441 lifts =  4,410 packets
                                                    ------
                                                    17,640 packets
```

Their 92,610 vertices are pairwise support-disjoint.  The packet histogram is

```text
size 5: 13,671
size 6:  3,528
size 7:    441.
```

There are 40 used exact prototypes and every exact prototype has precisely
441 lifts.  Under translations of `Z_42^2`, the first layer has five classes:
three size-five classes represented by respectively 4, 5, and 12 exact
prototypes, one size-six class represented by 8 prototypes, and one
size-seven class.  The ten surviving second-layer prototypes form one further
size-five translation class.

Every packet lies on an order-seven cyclic orbit.  Under affine
reparametrization `k -> a*k+b` of that orbit, the used packets have only three
unpointed midpoint-hypergraph types, one for each size 5, 6, and 7.  Marking a
red vertex gives five pointed types:

```text
size 5: three pointed types, with exact-template/role counts 62, 62, 31
size 6: one pointed type, with exact-template/role count 48
size 7: one pointed type, with exact-template/role count 7.
```

Without quotienting by any isomorphism there are 210 exact-template/literal-
role buckets.  This full classification is useful for audit, but the theorem
below needs only the unique size-seven prototype.

## 2. The unique seven-point prototype

Write its roles in cyclic order as

```text
p0=( 2,29)   p1=( 8,41)   p2=(14,11)   p3=(20,23)
p4=(26,35)   p5=(32, 5)   p6=(38,17).
```

Thus `p_(k+1)=p_k+(6,12) mod 42`.  A unit-weight balanced midpoint plan is

```text
(p1,p0,p6)
(p0,p1,p2)
(p0,p2,p4)
(p1,p3,p5)
(p3,p4,p5)
(p4,p5,p6)
(p2,p6,p3),
```

where `(x,y,z)` means `x+z=2y (mod 42)`.  Every endpoint is distinct from its
row's midpoint, every row has strictly positive squared endpoint cost, and
the sum of all seven potential-incidence vectors is zero.

For `(a,b)` in the nine-element set `BASE` and `s0,s1 in {0,...,6}`, its q=42
lift has role boxes

```text
d_(a,b,s0,s1,k)
  = (7a+s0, 7b+s1, p_k[0]+7a mod 42, p_k[1]+7b mod 42).
```

There are `9*7^2=441` such lifts, and their supports are mutually disjoint.
The displayed row plan transports to every lift.

## 3. Literal-role pigeonhole

Choose exactly one red vertex in every packed packet.  In each of the 441
size-seven lifts, record which transported literal role `p_k` is red.  There
are only seven choices, so one role occurs at least

```text
ceil(441/7)=63
```

times.  In particular two distinct lifts have the same exact template and
the same red role.  Pair their equal roles coordinatewise.  The common red
role gives a red-red word and every other role gives a blue-blue word, so all
seven paired words have even red parity.

The same argument actually works inside every one of the 40 exact-template
families: each has 441 copies and at most seven literal roles.

## 4. Stronger red-role alignment

The pigeonhole is not needed for the size-seven prototype.  If two lifts have
red roles `p_r` and `p_s`, there is a unique cyclic shift

```text
pi(p_k)=p_(k+s-r mod 7)
```

that sends red to red.  It sends every other (blue) role to a blue role and
preserves all modular midpoint identities.  Consequently **any two distinct
size-seven lifts**, with arbitrary red choices, can be paired by `pi` into
seven even-parity words supporting the transported balanced plan.

This is also why the pointed classification has only one size-seven type.

## 5. Physical horizon-two Farkas cycle

Let the two chosen lifts be `lambda` and `mu`.  Choose fixed offsets
`u,v in (0,1)^4`, common across the seven vertices within their respective
blocks, and define

```text
W_k = ((d_(lambda,k)+u)/42, (d_(mu,pi(k))+v)/42) in [0,1)^8.
```

The offsets are strictly interior, so every `W_k` has unique half-open
fine-box ownership.  Because the two symbol colors agree, each `W_k` lies in
the horizon-two even-parity language.

For every displayed prototype row `(p_i,p_j,p_l)`, use the global row

```text
(W_i,W_j,W_l).
```

Both four-dimensional blocks separately satisfy the exact torus midpoint
identity, with their own integer carries, because their within-block offsets
are common.  Hence the eight-dimensional row is an actual physical midpoint
row.  Its squared endpoint distance is strictly positive.

Suppose a single-valued function `F` on the physical horizon-two language
satisfied

```text
F(X)+F(Z) >= 2F(Y)+||X-Z||_2^2
```

on every actual torus-midpoint triple.  Sum this inequality over the seven
rows.  The coefficient of every `F(W_k)` is zero, while the sum of squared
costs is positive.  This gives `0>0`, a contradiction.  No boundedness,
continuity, measurability, additivity, or state-locality assumption on `F` is
used.

For the replay's fixed representative pair, the identity alignment has exact
aggregate cost `32/7`.  Across all 49 ordered red-role pairs, the seven cyclic
alignments give representative aggregate costs from `32/7` through `40/7`.
The verifier also checks every cyclic row-plan transport on all 441 lifts, so
strictness is not inferred from that representative alone.

## 6. Exact conclusion and scope

Proved:

1. the full 17,640-packet reconstruction and template/role classification;
2. the requested matching-template/matching-red-role pigeonhole;
3. the stronger arbitrary-red-role cyclic alignment;
4. an exact physical, common-offset, uniquely owned seven-row Farkas cycle at
   horizon two; and
5. nonexistence of any single-valued global coercive potential on this exact
   q=42 even-parity full-box language.

Not proved: a wall for every possible state-aware or overlapping multiblock
language; a carving-stable theorem after the seven full fine boxes are
arbitrarily trimmed; an EHPS shell; an improved lower bound for `r_3(N)`; or a
solution of Erdos Problem 142.

## 7. Replay

From the repository root on Windows:

```powershell
python -I certificates\erdos-142-q6-117-cell-disjoint-graph-carving-wall\horizon2-parity-wall\verify.py
```

Linux or WSL:

```text
python3 -I certificates/erdos-142-q6-117-cell-disjoint-graph-carving-wall/horizon2-parity-wall/verify.py
```

The success marker is

```text
PASS_Q42_HORIZON2_PARITY_WALL
```
