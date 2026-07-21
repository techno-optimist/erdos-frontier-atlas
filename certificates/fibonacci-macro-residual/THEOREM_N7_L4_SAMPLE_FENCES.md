# Sample fences for n=7 at L=4

Date: 2026-07-21

## Not exhaustive no-gos

| cell | sample | result |
|------|--------|--------|
| n=7 L=4 S=5 | 161 pad/mutate clocks | 5 routable, **5/5 LP-infeas** |
| n=7 L=4 S=6 | 161 clocks | 0 routable / 1200 outward |

Sealed minimal known for n=7 remains **L=5 S=5**.

## Contrast

n=7 L=5 S=5: WITNESS  
n=7 L=5 S=6: alternate WITNESS (larger S)

Artifacts: `N7_HUNT.json`.
