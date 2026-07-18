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
- **The frontier.** The scan was pushed to **no exception below `10¹⁰`** — extending the
  previously published frontier of `4·10⁷` (Jobling). That run lives in the foundry
  `verified-up-to-N` lane: reproduced Jobling's null result first, cross-checked the
  powerful-number counts against OEIS [A118896](https://oeis.org/A118896) at every power of
  ten through `10¹⁰`, sampled 400 witnesses (each re-factored by an independent code path),
  and is replay-verified. This in-repo verifier certifies the *method and the table*; the
  `10¹⁰` bound is the pinned foundry receipt (`a056828-mollin-walsh-*.json`).

## Reproduce

```sh
python3 certificates/erdos-1107/verify.py            # N = 10⁶
python3 certificates/erdos-1107/verify.py 2000000    # wider
```

## Honest scope

- This is a **verification-frontier** result, not a proof of the conjecture: it establishes
  that *no new exception appears below `10¹⁰`*, which is a first-class replayable
  contribution, but the finiteness conjecture itself is a WALL (no finite computation
  settles it).
- The `10¹⁰` extension is **not yet submitted to OEIS** — an external submission is a
  separate, human-sent step; this certificate records what we verified.
