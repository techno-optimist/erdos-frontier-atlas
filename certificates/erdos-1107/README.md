# Erdős #1107 / A056828 (Mollin–Walsh) — verification frontier

**Problem.** A *powerful* number has `p | n ⇒ p² | n` (1 is powerful). The Mollin–Walsh
conjecture asks whether every sufficiently large integer is a sum of **at most three**
powerful numbers — equivalently, whether the exception set (OEIS
[A056828](https://oeis.org/A056828)) is finite. The only known exceptions are
**{7, 15, 23, 87, 111, 119}**.

## What is certified

- **The exception table.** [`verify.py`](verify.py) recomputes the exceptions over `[1, N]`
  by an exact bitset sumset and confirms they are *exactly* `{7, 15, 23, 87, 111, 119}`
  (default `N = 10⁶`, ~10 s, dependency-free). All six are `< 120`, so no seventh exists
  below `10⁶`.
- **The public frontier.** This repository certifies **no seventh exception below `10⁶`**.
  A private `verified-up-to-N` run separately reported no seventh exception through `10¹⁰`,
  with A118896 and sampled-witness cross-checks. The 2026-07-21 honesty audit could not
  locate the cited canonical receipt in the public package, so `10¹⁰` is quarantined as
  private operational evidence until the runner and receipt ship together. It is not a
  public claim of this certificate.

## Reproduce

```sh
python3 certificates/erdos-1107/verify.py            # N = 10⁶
python3 certificates/erdos-1107/verify.py 2000000    # wider
```

## Honest scope

- This is a **verification-frontier** result, not a proof of the conjecture: it establishes
  only the chosen finite replay range (default `10⁶`). The finiteness conjecture itself is
  a WALL; no finite computation settles it.
- The private `10¹⁰` run is not yet a public artifact and is not submitted to OEIS.
