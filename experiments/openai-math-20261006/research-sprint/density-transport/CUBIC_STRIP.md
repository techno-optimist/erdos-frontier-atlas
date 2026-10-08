# Kernel-checked algebra for the growing cubic strip

`CubicStrip.lean` is an independent Std-only module, checked with official
Lean 4.33.1. It proves the algebraic consequences of an **explicit supplied
integer quotient identity**. It does not formalize Kummer's formula, the
prime-power reduction, or the derivation of this identity from a P699 failure.
It assumes no external OpenAI theorem or custom axiom.

Write `P=(n-1)(n-2)`. For integers `n>=3`, `d>=4`, and `m`, supply

    m*P = d*(3n-d²-2),     d² != 3n-2.

The checked module proves:

- The exact sum-of-squares identity
  `4(P-d(3n-d²-2))=(2n-3d-3)²+4(d-4)³+39(d-4)²+110(d-4)+71`.
  Thus `P-d(3n-d²-2)>0` for every integer `n` when `d>=4`.
- `m<=-1`, followed by `d³>=n²+(d-1)(3n-2)>n²`.
- More generally, the supplied bound `m<=-r` implies
  `d³>=r*n²+(d-r)(3n-2)`, for any integer `r`.
- If the supplied quotient is even, then `m<=-2` and
  `d³>=2n²+(d-2)(3n-2)>2n²`.
- If the supplied quotient is divisible by four, then
  `d³>=4n²+(d-4)(3n-2)`. This statement is non-strict because the
  displayed margin vanishes when `d=4`.
- If `n=4a` and `d=2b` for integers `a,b`, then `d²!=3n-2`,
  discharging the nonzero premise. Connecting these parity hypotheses
  to the arithmetic application remains a separate step.
- With the additional supplied identity `m=4g³k-d`, `g>=0`, and
  `k>=1`, one gets `4g³<d`. The formal parameter `g` is an integer;
  the module does not assert it is a gcd or construct `k`.

The formal countermodel `zero_quotient_control` uses `n=6,d=4,m=0`:
the quotient identity and size assumptions hold but the coefficient-one
conclusion fails. Thus the nonzero premise cannot simply be discarded.

Replay from the repository root:

```sh
python3 -I experiments/openai-math-20261006/research-sprint/density-transport/verify_cubic_strip.py --lean /tmp/erdos-density-lean/lean-4.33.1-darwin_aarch64/bin/lean
```

The executed command compiled successfully and audited all ten theorem
dependencies. The nine algebraic theorems use only the standard Lean axioms
`propext`, `Classical.choice`, and `Quot.sound`; the concrete countermodel uses
no axioms. There is no `sorry`, `admit`, or custom axiom declaration.
`cubic-strip-execution.json` binds the source, verifier, executable, and local
compiled artifact hashes. `cubic-strip-axiom-audit.log` preserves the compiler's
dependency audit. These receipts are separate from the density-transport proof.

Verified source SHA-256:
`2aeb918e00adf8526ae56020894523ea041a2967253c058c2799c8b27b00a732`.
