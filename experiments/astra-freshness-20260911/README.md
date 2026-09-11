# Erdős atlas freshness — 2026-09-11

Not a production-graph rewrite. Overlay only. Compare YAML informal states, not Lean suffixes.

## Pins

- Previous audited upstream: `2a4d12b8be30a0483f49259654d10fcb0e2f08eb` (2026-09-04).[11]
- Current `teorth/erdosproblems` main: `3c68e941162f81d650fc886eed34e58bed3a6a01` (2026-09-09T17:51:07Z).[10]
- Both YAML dumps have **1,217** records. Homepage reports **1,220** problems, **586 (48%)** solved — different snapshot, not silently reconciled.[1]

## Informal mathematical changes since 2026-09-04 (3)

| # | YAML before → after | Live banner (browser 2026-09-11) | Notes |
|---|---|---|---|
| 477 | open → solved | **SOLVED** | GPT (Price / pipeline-math): such an A exists for f(n)=n^d, even d≥6. YAML commit `b17335bedd` 2026-09-05.[6][10] |
| 625 | open → solved ($1000) | **SOLVED - $1000** | Petkov and GPT-5.6: almost surely χ−ζ ≫ n/(log n)^3. Same YAML commit.[7] |
| 501 | open → independent | **INDEPENDENT** | Glazer: first question independent of ZFC. YAML commit `56d4286e6d` 2026-09-07.[8] |

Homepage OPEN→SOLVED list still shows **477 625 (05/09/26)** and still lists **501** on 03/09/26; YAML now matches 477/625 as solved and 501 as independent. The 03/09 listing of 501 was a catalog-date, not an informal “solved”.[1]

Six further YAML rows only changed the formal suffix `(formalized)` → `(Lean)` (#1, #74, #126, #548, #557, #571). Not new solutions.

## Still open (checked live + YAML)

- **#699** FALSIFIABLE.[2]
- **#376** OPEN. Infinitude of n with C(2n,n) coprime to 105. Graph cell: next A030979 term > 10^70; infinitude is a wall.[9]
- **#993, #743** remain FALSIFIABLE; **#366** VERIFIABLE.

## Graph is stale (do not silently regenerate)

Production cards still say #1 upstream Open / movable, #548 falsifiable trap. Those informal states moved on 2026-09-03 (already in the 09-04 overlay) and this overlay does **not** rewrite `atlas/graph/` or `views/graph/`.

Machine-readable: `upstream-diff.json`.
