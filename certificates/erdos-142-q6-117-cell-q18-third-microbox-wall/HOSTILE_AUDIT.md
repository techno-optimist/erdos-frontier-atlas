# Hostile audit: q=18 disjoint microbox obstruction packing

Audited source:

- D:\p42_research\microcarve_transfer_20260818
- search_disjoint_packets.py SHA-256:
  94effecacb0734e08e4a63f0a25b86f2538c74f02d1386471b4ae6bbe9787cf1
- verify_microbox_dilation_cover.py SHA-256:
  b9f5ad39e94d90500d5bda4d289210b5b94dd4a3de3a13707509a5454d83ea13

## Verdict

**APPROVE.** The mathematical theorem, deterministic discovery
reconstruction, frozen semantic certificate, and independent
standard-library replay are sound. No physical-label, carry, raw-cost,
disjointness, dependency, or gate-arithmetic gap was found.

The frozen certificate is:

- D:\p42_research\microcarve_transfer_20260818\frozen_semantic_certificate.json
- SHA-256:
  e445d0ca22b7c0dcca087bb6bfea60b94cdf30669e59d8b60ea4c9f96e95a18c

The separately written no-import replay is:

- D:\p42_research\erdos142_q18_packing_hostile_audit_20260818_a\independent_replay.py
- SHA-256:
  c466af4935b99a60d56d93b8d8eda1d2977775da976af7622a6938d105e3d883

It passes under native Windows Python and WSL Python 3.

## Exact result checked

The q=18 refinement contains

\[
117\cdot3^4=9477
\]

distinct physical half-open microboxes. The deterministic run produced:

- 433 pairwise vertex-disjoint componentwise-dilation edges, using 866 boxes;
- 114 mutually vertex-disjoint common-offset midpoint packets;
- no packet vertex used by a matching edge;
- 547 pairwise-disjoint obstruction supports in total.

Every feasible complete-microbox support must delete at least one box from
each obstruction, so it deletes at least 547 boxes and retains at most 8930.
The exact gate is

\[
\frac{49}{576}18^4=\frac{35721}{4}=8930.25.
\]

Thus 8930 is strictly below gate. Conversely, a strictly above-gate integer
box count would be at least 8931 and allow at most 546 deletions.

The terminal reconstruction matched the claimed digest:

    PACKING_TOTAL dilation=433 packets=114 obstructions=547
    CERTIFICATE_DIGEST 25f5f0e5dd40ad0641d38009148bd2b5fcd742645bdfb1d98e1c3f0e0d18182e
    DENSITY_WALL forced_deletions=547 allowed_deletions=546 max_retained=8930 gate_count=8930.25
    EXACT_DISJOINT_PACKING_WALL_R3

## Physical midpoint audit

The universe map is

\[
(c,s)\longmapsto d=3c+s\in\{0,\ldots,17\}^4.
\]

The 117 coarse cells are distinct, and refinement makes the 9,477 q=18 digit
vectors distinct. Hence a packet vertex is a unique physical microbox, not an
abstract repeated label.

For every packet row, the replay checks

\[
d_x+d_z-2d_y\equiv0\pmod {18}.
\]

For any common \(u\in(0,1)^4\), use the actual canonical points

\[
x=(d_x+u)/18,\quad y=(d_y+u)/18,\quad z=(d_z+u)/18.
\]

They lie in the strict interiors of their respective boxes and satisfy the
torus midpoint equation because the common offset cancels. Their required
raw-canonical endpoint cost is exactly

\[
\lVert x-z\rVert_2^2
=18^{-2}\sum_j(d_{x,j}-d_{z,j})^2.
\]

The selected integer numerator is recomputed and required to be positive.
The exact positive integer nullspace weights cancel

\[
\sum_{\text{rows}}w(1_x+1_z-2\,1_y)
\]

at every unique physical digit vertex. Summing the actual inequalities
therefore gives zero on the potential side and a strictly positive raw-cost
sum. This rules out an arbitrary finite single-valued physical potential if
all boxes of that packet survive; boundedness, continuity, affinity, and
cellwise constancy are not used for packet rows.

The common-offset family is full four-dimensional measure inside each
individual microbox under the map \(u\mapsto(d+u)/18\). It is still a
lower-dimensional synchronized family in triple space, so pointwise
coercivity is essential. The theorem does not extend to an almost-everywhere
requirement.

## Dilation-edge audit

Each selected edge comes from a valid oriented coarse dilation pair. In every
active coordinate the first microbox uses residual subindex zero and the
second uses subindex two; every inactive coordinate uses the same subindex.

With \(T=1/(2r)=1/6\) and \(t_j=T/3^j\):

- \(t_j,3t_j\) lie strictly in the low residual third;
- \(1-t_j,1-3t_j\) lie strictly in the high residual third;
- inactive coordinates can use any fixed interior residual in their common
  microinterval.

The two actual rows give

\[
D(3t)-D(t)\ge K(72-48t),\qquad K\ge1.
\]

Finite telescoping grows linearly and contradicts boundedness of the physical
correction. Therefore every retained pair is an obstruction and any feasible
support must delete one endpoint.

The graph used is a valid subset of all q=18 strict-dilation adjacencies; it
need not enumerate every possible fine-grid adjacency for a lower-bound
packing argument.

## Disjointness audit

The 433 matching edges are found independently in connected components of at
most nine vertices by exhaustive subset enumeration. Their flattened endpoint
set has size 866.

Packet discovery begins with all matching endpoints unavailable. Each packet
is a sink strongly connected component of a deterministic midpoint map:

- every packet vertex has one positive-cost midpoint row;
- both endpoints of every selected row remain inside the same packet;
- exact balance has one-dimensional nullspace with all weights strictly
  positive.

After accepting a packet, every packet vertex is removed from availability.
Sink SCCs in one iteration are mutually disjoint. Final assertions check that
all packet vertices are unique and disjoint from the 866 matching endpoints.
Thus the 547 support sets are genuinely pairwise disjoint.

## Dependency and exhaustiveness audit

- The dilation cover/matching components are finite and exhaustively searched.
- NumPy is used for bounded integer digit enumeration and deterministic
  maximum-cost row selection; no floating comparison enters an accepted
  modular defect, incidence, or right side.
- SymPy computes rational nullspaces. Denominators are cleared to exact
  positive integers, after which all incidence and cost claims are replayed
  with Python integers.
- The exploratory SciPy CEGAR file is not imported by the decisive script.
- No claim that all possible packets or all possible dilation edges were
  found is needed. A packing of 547 verified disjoint obstructions alone
  proves the deletion lower bound.

Native Windows replay passed. The standard-library dilation verifier also
passed under WSL. The packet discovery script did not run under this WSL
installation because NumPy is absent; this is an environment dependency, not
a mathematical failure.

## Frozen replay resolution

The discovery script originally constructed an in-memory certificate object
and printed only its SHA-256 digest. This was not sufficient for independent
replay. The resolved packet now freezes:

- all 433 matching edges as physical microbox labels or q=18 digit vectors;
- every packet row, positive integer weight, and semantic packet support;
- a hash binding the exact frozen bytes.

The separate standard-library verifier reconstructs the 117-cell alphabet,
validates every record directly, checks exact physical incidence and raw
cost, checks all cross-support disjointness, replays the finite dilation
telescope, redoes the gate arithmetic, and rejects planted corruptions. Its
terminal output begins:

    PASS_INDEPENDENT_Q18_MICROBOX_PACKING_WALL

The discovery NumPy/SymPy stack is therefore no longer part of the trusted
replay path.

## Scope

The theorem closes arbitrary unions of complete globally aligned residual
third-microboxes in the fixed 117-cell one-block geometry, under bounded
single-valued pointwise raw-canonical coercivity.

It does not close:

- pieces properly carved inside q=18 microboxes;
- fourth-grid or finer subdivisions;
- deformed, overlapping, or non-axis-aligned tiles;
- context-owned or path-dependent word languages;
- coupled multi-block tiles;
- almost-everywhere coercivity;
- integer transfer.
