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

Stack: 135 ← … ← 147 ← 148.

Open for i=3: residual only for \(n\not\equiv 3\pmod 4\), and Type B2b \(P^+\le n/10\). Then i≥4. Next binomial cell on the graph: **#376** (Kummer 105).
