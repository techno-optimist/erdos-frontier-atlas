# Astra campaign stack (2026-09-04 → 2026-09-11)

All open, CI green, unmerged. Not a solution of #699.

| PR | Branch | What it actually is |
|---|---|---|
| [#135](https://github.com/techno-optimist/erdos-frontier-atlas/pull/135) | `agent/astra-structural-probes-20260904` | P699 near-central strip, P993 probes, official freshness |
| [#136](https://github.com/techno-optimist/erdos-frontier-atlas/pull/136) | `agent/astra-briefcase-transfers-20260904` | tail transfer, blocks, CRT bridge, P699 diagonals |
| [#137](https://github.com/techno-optimist/erdos-frontier-atlas/pull/137) | `agent/astra-lean-seed-20260904` | kernel adjacent-binomial gcd |
| [#139](https://github.com/techno-optimist/erdos-frontier-atlas/pull/139) | `agent/astra-i2-family-20260911` | kernel i=2, n=2j+3 family |
| [#140](https://github.com/techno-optimist/erdos-frontier-atlas/pull/140) | `agent/astra-substrate-20260911` | method substrate over the attack graph |
| [#141](https://github.com/techno-optimist/erdos-frontier-atlas/pull/141) | `agent/astra-i2-complete-20260911` | complete i=2: gcd(C(n,2),C(n,j))≥2 |
| [#142](https://github.com/techno-optimist/erdos-frontier-atlas/pull/142) | `agent/astra-i3-20260911` | i=3 gcd≥2; odd when n≡3 (mod 4) |
| [#143](https://github.com/techno-optimist/erdos-frontier-atlas/pull/143) | `agent/astra-i3-residual-20260911` | coprime-to-j! cancel |
| [#144](https://github.com/techno-optimist/erdos-frontier-atlas/pull/144) | `agent/astra-i3-close-20260911` | coprime-6 cancel; n=2p only (10,5) |
| [#145](https://github.com/techno-optimist/erdos-frontier-atlas/pull/145) | `agent/astra-i3-typeA-20260911` | Type A: P+(o)>n/4 only (10,5),(16,7) |
| [#146](https://github.com/techno-optimist/erdos-frontier-atlas/pull/146) | `agent/astra-i3-typeB1-20260911` | Type B1: n/6<p≤n/4 only (65,15); STACK.md |
| [#147](https://github.com/techno-optimist/erdos-frontier-atlas/pull/147) | `agent/astra-i3-typeB2a-20260911` | Type B2a: n/8<p≤n/6 empty |
| [#148](https://github.com/techno-optimist/erdos-frontier-atlas/pull/148) | `agent/astra-i3-mod4-band89-20260911` | n≡3 (mod 4) residual empty; p-band 8–9 |
| [#149](https://github.com/techno-optimist/erdos-frontier-atlas/pull/149) | `agent/astra-freshness-376-20260911` | catalog delta 477/625/501; #376 Kummer checker |
| [#150](https://github.com/techno-optimist/erdos-frontier-atlas/pull/150) | `agent/astra-376-search-20260911` | #376 A030979 complete through 3^24 |
| [#151](https://github.com/techno-optimist/erdos-frontier-atlas/pull/151) | `agent/astra-376-csearch-20260911` | #376 C search complete through 3^31 |
| [#152](https://github.com/techno-optimist/erdos-frontier-atlas/pull/152) | `agent/astra-376-d35-20260911` | #376 C search complete through 3^35 (bounded replay; do not extend D) |

Stack: 135 ← … ← 151 ← 152.

**Goal:** method substrate, not a scoreboard. See `GOAL.md`.

Open for i=3: Type B2b leftover is \(n-1\) with at least two distinct odd primes (or \(n\equiv 1\pmod 4\), or \(n\equiv 4\pmod 6\)). Prime-power \(n-1\) is empty. #376: infinitude idea, not \(D=36\).
