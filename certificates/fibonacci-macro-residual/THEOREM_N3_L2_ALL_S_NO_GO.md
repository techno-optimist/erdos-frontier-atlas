# All-S no-go for n=3 length-two globally compensated macros

Date: 2026-07-20

## Theorem

There is no common-anchor, split-weight, length-two, globally Parikh-balanced
Fibonacci macro for the primitive `n=3` circuit on **any** deterministic
ternary clock.

## Proof architecture

Any L=2 return from the diagonal anchor only uses:

- the anchor state `0`,
- a mid-image `M = im(f)` with `|M| ≤ 3` (first-layer transitions from the
  anchor),
- the endpoint states of the four injective tag ports.

Hence the used state set has size at most `1+3+4 = 8`.  It is enough to
rule out every used-state configuration of size ≤8.

### Layer A — ambient clocks with ≤4 states (exact census)

For every deterministic clock with `S ∈ {2,3,4}` in which all states are
L≤2-reachable from the anchor, every injective tag-port assignment is
checked.  Real LP feasibility of exact column weights plus Parikh balance
is required for a positive cell.

| S | clocks | routable | real-LP feasible |
|--:|--:|--:|--:|
| 2 | 64 | 0 | — |
| 3 | 19 683 | 52 | 0 |
| 4 | 16 777 216 | 2 112 | **0** |

Artifacts: `N3_L2_S2_EXHAUSTIVE_RESULT.json`,
`N3_L2_S3_EXHAUSTIVE_RESULT.json`, `N3_L2_S3_CONE_RESULT.json`,
`N3_L2_S4_FAST_RESULT.json`.

Any construction whose **used** state set has size ≤4 embeds into Layer A.

### Layer B — MIP over mid image and free tag ends (capacity 8)

Relabel so the mid image is one of the WLOG models:

1. `M ⊆ {0,1,2}` (may include the anchor), or
2. `M = {1,2,3}` (anchor not a mid; pure three-mid image).

Tag endpoint states are free in `{0,…,K−1}` with `K=8` (capacity), subject
to port injectivity.  For every outward-legal digit pattern, a HiGHS MIP
enforces:

- exact split weights,
- deterministic `f` and `g`,
- global Parikh balance,
- endpoint linking of every selected unit route.

Results:

| mid model | K | digit patterns | status |
|---|--:|--:|---|
| `{0,1,2}` | 5 | 11 | all INFEAS |
| `{0,1,2}` | 8 | 11 | all INFEAS |
| `{1,2,3}` | 8 | 11 | all INFEAS |

Artifacts: `N3_L2_FREE_TAGS_MIP_RESULT.json`, `N3_L2_MID123_RESULT.json`.

Mid images of size 1–2 (pools `{0}`, `{1}`, `{2}`, `{0,1}`, `{1,2}`) with free
tag ends in `{0..7}`: **all digit patterns INFEAS**
(`N3_L2_SMALL_MID_RESULT.json`, status `ALL_INFEAS_SMALL_MID`).

## Conclusion

Layers A and B exhaust the L=2 used-state geometry.  Therefore no n=3 L=2
common-anchor split-weight Parikh-balanced macro exists on any clock.

## Contrast

| cell | status |
|---|---|
| n=2, L=2 | **exists** (prior witness) |
| n=3, L=2 | **impossible** (this theorem) |
| n=3, L=3 | **exists** (`THEOREM_N3_L3_SPLIT_MACRO_WITNESS.md`) |

## Scope

Common-anchor, split-integral unit returns, deterministic ternary clocks.
Does not address non-common-anchor architectures or non-split fractional
flows outside the integral macro model.

## Replay

```powershell
python search_n3_l2_s4_fast.py
python mip_n3_l2_free_tags.py
# mid={1,2,3} companion already written to N3_L2_MID123_RESULT.json
python verify_n3_l3_macro_witness.py   # positive L=3 contrast
```
