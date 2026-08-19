# Weighted multiset 7-sunflower screen

Scratch-only theorem and verification packet.  Nothing here is part of a PR.

Start with [THEOREM.md](THEOREM.md).  It proves:

* exact equivalence of the repeated-pattern multiset obstruction with
  antichain plus ordinary distinct 7-sunflower avoidance;
* tensor closure and weighted-mass multiplicativity;
* uniformization at the exact base `597/40`;
* `M_1=6`, `M_2=42` with the explicit `2 K_7` witness, and the strengthened
  recursion `M_k <= 6(k M_{k-1}-(k-1))`;
* an exact rational LYM/cap LP: total safe-family optimum `1` through
  dimension 28 and no gate violation through dimension 31.

The LP first exceeds `1` at dimension 29 and first exceeds the gate at
dimension 32.  Those are relaxation failures, not constructions.

Run [run.ps1](run.ps1) to replay the standard-library verifier and integrity
checks.  This packet is a support-level packet screen only; it makes no claim
of a physical potential.

[FINITE_STATE.md](FINITE_STATE.md) records the separate regular-language
probe.  Unrestricted regularity is equivalent to the finite-block question,
but a synchronized-product exhaustion proves that every globally safe complete
binary DFA with at most three states has mass at most one at every length.
