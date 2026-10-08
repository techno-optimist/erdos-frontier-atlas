# Formal algebra for seven diagonals

`DiagonalInequality.lean` proves three explicit-hypothesis algebraic statements
under Lean 4.33.1 using only Std. It verifies positivity for d=4,8,...,28,
rejects the resulting weak failure inequality, and rejects the stronger version
with a gcd-sized parameter g>=2. The audited axioms are propext and Quot.sound.

These are the final algebraic steps of the initial seven-diagonal proof.
They do not formalize prime-power localization, the reduced cubic divisibility,
or the full P699 statement. The stronger integrality argument in the
[arithmetic note](../arithmetic/README.md) adds d=32 and the growing strip;
its d=32 proof uses a different premise.

`negative/ExtendTo32.lean` deliberately asserts a false polynomial inequality
at n=348,d=32. Its rejection is expected. This is not a P699 counterexample.

Replay with `python3 verify.py --lean /path/to/lean-4.33.1/bin/lean`.
The default replay does not rewrite receipts. `--record` writes fresh local
execution metadata; `execution.json` and the audit logs preserve this run.
