# F130: exact uniform Fourier source audit

Source pin: OpenAI/math commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`. This is a source and statement audit, not a local Lean verification, executable extraction or performance result. All mathematical source material here is public primary-source material; no applied measurement evidence is included.

## What is quantified

The [comparator specification](https://github.com/OpenAI/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/ComparatorChallenges/UniformFourier.lean) defines

`DFTGoal := ∃ order solve W, DFTProgram order solve W ∧ TimeBounds W`,

and an analogous convolution goal. `order` and `solve` are single finite programs, quantified before the input length. Each program property supplies one exponent `cBound` and requires correctness for every natural `n > 0` and every complex input vector (every pair of vectors for convolution). Its work allowance `W n` does not depend on vector entries. Thus this selected uniform statement is all-positive-length, not merely subsequential. The [scope document](https://github.com/OpenAI/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/130.md) also discusses a separate, subsequential circuit theorem; the two statements should not be conflated.

For the DFT, the exact output is the length-`n`, positive-sign, unnormalized canonical transform:

\[
  y_j=\sum_{k=0}^{n-1}\exp(2\pi i/n)^{jk}x_k.
\]

For convolution the output has length `2*n-1` and coefficient `k` is the sum of `x_r*y_s` over `r+s=k`. Zero-length input is outside the quantified correctness premise.

Writing `d = run order n` and `cap=(n+2)^cBound`, the DFT property requires `d.valid`, positive `d.val < 1024*n^3`, integer peaks bounded by `cap`, and `W n + 10*(n+2) ≤ cap`. For every vector it runs

`solve (n, root d.val, inputTape)`

and requires valid execution, its peak bound, exact output equality, and `d.work + 1 + result.work ≤ W n`. Convolution has the corresponding root-order bound with `2*n-1`. The actual [Main.lean](https://github.com/OpenAI/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/OAI/Computability/FourierTransform/Main.lean) additionally proves `_order` variants with the explicit `receipt` function and stronger bounds `<8*n^3` and `<8*(2*n-1)^3`.

`TimeBounds` simultaneously requires big-O of the stated paper bound, big-O of

\[
n(\log n)^{1-10^{-13}},
\]

and little-o of `n log n`. The paper exponent is

\[
\theta=\log(M-\Delta/W_0)/\log M,
\quad M=10^6,\;W_0=2^{71},\;\Delta=6871402692000000,
\]

with paper time `n (log n)^theta (log log n)^(4-theta)`. These are asymptotic operation bounds, not a numerical crossover, finite-size speedup or wall-clock claim.

## Root and coefficient model

The required scalar input is the **specified canonical root** `exp(2*pi*i/d.val)`, not an arbitrary primitive root and not a floating approximation. The order program computes the order from length alone. The theorem charges `d.work`, a single root-provision unit, and the solver's work. It does not construct an exact complex root in a bit model or validate an arbitrary supplied root at runtime. Scalar preparation from this root is included in the solver semantics. This distinction is explicit in [Goal.lean](https://github.com/OpenAI/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/OAI/Computability/FourierTransform/Goal.lean).

The [RAM syntax and semantics](https://github.com/OpenAI/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/OAI/Computability/FourierTransform/RAM.lean) charge unit-cost exact complex addition/subtraction, scalar multiplication and scalar inversion; prepared denominators must be nonzero along valid runs. This validity condition is proved, not implemented as a complex-zero test. There is no instruction for an arbitrary complex literal. Available scalar constants start with zero/one and the supplied root, and coefficients can be prepared using exact operations. “Unrestricted coefficients” concerns their magnitude/representation/conditioning, not permission for a per-length table of free arbitrary complex constants.

The transform program's type forbids general data-data multiplication. Convolution permits a typed left-input × right-input product; scalar/data and left/right/both registers remain distinct. Integer arithmetic, comparison, indexing, loops, stack overhead and array initialization/writes are charged. Natural subtraction/division/remainder use their stated Lean semantics, including defined zero-divisor cases for the integer operations; scalar inversion instead records a nonzero validity condition.

Polynomial integer/peak/work bounds yield logarithmic-size integer/address words in the declared RAM convention. They do **not** bound the bit length or magnitude of complex coefficients, establish numerical stability, or make exact complex arithmetic constant-time on physical hardware. [RegisterBounds.lean](https://github.com/OpenAI/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/OAI/Computability/FourierTransform/RegisterBounds.lean) proves the typed integer-register preservation statements. Arrays represented mathematically by `Fin` functions are interpreted as RAM cells; these definitions are not a claim about evaluation speed of generated Lean code.

## Proof source versus challenge

The comparator file deliberately ends the two target theorems with `sorry`; it is the challenge specification, not the submitted proof. The [comparison configuration](https://github.com/OpenAI/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/ComparatorChallenges/UniformFourier.json) selects `OAI.Computability.FourierTransform.Main`, theorem names `OAI.PowerSaving.transform_main` and `OAI.PowerSaving.convolution_main`, and permitted axioms `propext`, `Quot.sound`, `Classical.choice`. It requests no separately named definition comparisons and sets `enable_nanoda:false`; no Nanoda run should be inferred.

Main gives proof terms through `transform_main_order`/`convolution_main_order`, `flagshipOne`/`flagshipBoth`, and asymptotic estimates. Its comment states that the concrete construction uses 32 binary coordinates per factor, 4,060 triples and a `2^50` role envelope, with a stronger saving sufficient for the stated constants. Its exclusions are explicit: general rational-algebra extraction, symbolic certificate search, circuit printing, and bounded-printer uniformization from the synthesis appendix are not formalized by these selected statements. This does not negate their fixed-program uniformity; it limits which further synthesis assertions one may transfer.

## Bounded checks performed here

The snapshot contains 97 public source/configuration files, 645,234 bytes, including the 89 local proof modules reached by line-leading imports from Main: 88 FourierTransform modules and FourierCircuit/Core. All proof import lines in this snapshot have the simple one-module form followed by the scan. The only external proof import found is `Mathlib`; package sources or caches were not fetched.

The complete RAM block in challenge and solution matches after comment/whitespace removal. Sixteen principal goal, transform/convolution and time definitions likewise match under that textual check. A lexical scan of the 89 local proof modules found no `sorry`, `admit`, `axiom`, `unsafe` or `native_decide` tokens outside comments/strings. Neither this scan nor a matching theorem name checks the elaborated declaration graph, imported axioms, compiler environment or proof validity. No theorem was compiled or exported here. See `source-manifest.json` and `static-source-checks.json` for exact byte pins and scope.

## One precise next step

**Prepare and execute a declaration-level audit of only the two F130 target theorems in an isolated pinned environment.** Preserve this source snapshot unchanged. Use Lean `v4.34.1` and mathlib commit `d13f23b723b8a846827a245b89c10fc7d3f11612`, with mathlib's own transitive package pins recorded. Check available toolchain/dependencies first; if missing, return an explicit resource/setup requirement rather than starting an unrestricted download.

Do not innocently invoke the repository-wide Lake configuration: its [lakefile.lean](https://github.com/OpenAI/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/lakefile.lean) has a `run_cmd` pre-resolution hook capable of cloning and patching numerous unrelated dependencies before ordinary commands. An isolated project may retain the identical 89 source modules and depend only on their required pinned Mathlib closure; record that isolated build configuration as an audit input. It is a changed build environment, not a changed proof source.

Build only Main and its actual imports, then compile the supplied, currently unrun `AuditUniformFourier.lean` to print the target types, key predicates and transitive axiom lists. Require no `sorryAx` or axiom beyond the permitted set. Preserve the elaborated declarations/export and all exact input/output/tool hashes. In separate challenge/solution environments, run the configured comparator with pinned comparator/landrun/lean4export versions, so its statement/dependency comparison is actually observed; do not import the placeholder challenge into the proof environment or count a placeholder build as success. The upstream [Comparator README](https://github.com/OpenAI/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/ComparatorChallenges/README.md) describes the intended tool chain, but those tools have not been installed or run here.

Acceptance is narrowly: the exact target declarations compare and check with the recorded permitted axiom/dependency closure in that environment. It would not establish the omitted synthesis appendix, root-generation bit complexity, conditioning, practical speed, executable quality or novelty. No benchmark or speedup experiment is the proposed next step.
