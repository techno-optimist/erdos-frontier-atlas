# Checked bridge from positional blocks to the cubic strip

`FormalBridge.lean` closes the formal gap between **explicit finite positional
block data** and the previously checked cubic-strip inequalities. It constructs
the positive quotient and the polynomial identity; neither is an assumed axiom
or a premise of the final theorem. This remains a conditional arithmetic theorem,
not a fully formal proof starting from failure of P699.

All variables in the main theorem are integers. Put
`Q=u(v-u)(v-2u)` and `P=(n-1)(n-2)`. The theorem `strip_from_blocks` takes:

- `n>=3`, `d>=4`, `g>0`, `u>0`, `v>2u`, `n=gv`, `j=gu`,
  `d=n-2j`, and an integer witness for `4|n`.
- Two finite lists of blocks `bs,cs`. `CoprimeBlocks` says each block is
  coprime to the product of the later blocks in its list.
- At position `t=1` for `bs`, and `t=2` for `cs`, every block `M` divides
  `n-t` and divides `j-r` for some integer `0<=r<=t`.
  `localAt_of_residues` converts the usual hypotheses `M>0`, `M|(n-t)`,
  and `j mod M<=t` to this formulation.
- With `B=product(bs)` and `C=product(cs)`, the small-factor data
  `gcd(C,4)=1`, `D=2 or 6`, `gcd(D,BC)=1`, and `P=D*B*C`.
  If `D=6`, require `3` not to divide `n`.

It concludes

    d³ >= 2n² + (d-2)(3n-2) > 2n²,     d > 4g³.

The parameter `g` need only be a positive common scaling factor. Being the
greatest common divisor, or having coprime `u,v`, is unnecessary for the
formal implication; choosing the actual gcd gives the strongest application.

The proof transports each positional congruence through `nu=vj`, avoiding
division modulo a block. Coprime block assembly yields `B|u(v-u)` and
`C|4Q`. It also proves `gcd(B,C)=1` from their divisibility into the consecutive
integers `n-1,n-2`. It cancels the factor 4 against `C`, proves `2|Q`
unconditionally and `3|Q` when `3` does not divide `v`, and restores the
omitted factor `D`. Thus `P|Q`. Positivity constructs `k>=1` with `Q=Pk`,
and polynomial algebra constructs

    (4g³k-d)P = d(3n-d²-2).

The imported checked module `CubicStrip` then supplies the strip and gcd gap;
the bridge proves the required nonzero and even-quotient premises from the
given scaling and parity data. Its sum-of-squares positivity proof is rebuilt
from source during verification.

`strip_from_blocks_two` specializes to `D=2` and removes the modulo-three
premise. This can be reused wherever the relevant arithmetic supplies those
two block lists and factor data, including proposed higher-index transfers.
It makes no claim that such a transfer's input data have already been proved
from binomial coefficients.

## Remaining formal boundary

The module does not formalize Kummer's formula, derive the block residues from
absence of a common odd prime divisor of binomial coefficients, enumerate full
prime-power blocks, or establish the stripped factorization data from that
enumeration. The earlier informal arithmetic argument supplies those steps.
The formal blocks are arbitrary integers satisfying the stated conditions;
no imported prime-power or external OpenAI theorem is silently assumed.

## Verification

```sh
python3 -I experiments/openai-math-20261006/research-next/formal-bridge/verify.py --lean /tmp/erdos-density-lean/lean-4.33.1-darwin_aarch64/bin/lean
```

Official Lean 4.33.1, `Std` only. The verifier rebuilds the pinned local
`CubicStrip.lean` dependency and this module into this directory's ignored
`.build/`, audits all 16 bridge theorems, and permits only the standard Lean
axioms `propext`, `Classical.choice`, and `Quot.sound`. No source contains
`sorry`, `admit`, or custom axiom declarations.

Two deliberately false controls must be rejected by the kernel: multiplying
noncoprime divisors (`2|2` twice does not imply `4|2`), and restoring the factor
3 without the missing hypothesis (`n=4,u=1,v=3,B=C=1,D=6` gives `Q=2`).
The second control satisfies every premise of `restore_cubic` except its
modulo-three condition. It concerns that isolated lemma, not a P699 example.

`execution.json` records commands, source and executable hashes, imported
dependency hash, compiled artifact hashes, and control outcomes.
`axiom-audit.log` and `negative-controls.log` preserve compiler output.
These are local proof receipts; no public problem status or literature novelty
is established by them.
