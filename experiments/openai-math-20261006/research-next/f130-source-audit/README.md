# F130: source audit for uniform exact Fourier programs

This packet preserves public mathematical source at OpenAI/math commit
`fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` and replays bounded byte, import and
textual checks. **It does not contain a Lean build, comparator run or empirical
speedup result.**

The selected theorem specifies fixed finite programs for every positive input
length in an exact complex-arithmetic RAM model. Root-order selection and scalar
preparation are charged, while the specified canonical root is supplied as an
input. Coefficients have no magnitude/conditioning/bit-cost bound. The selected
statements exclude the general extraction, symbolic search and printer
uniformization from the synthesis appendix. See the [scope audit](snapshot/F130_SCOPE.md)
and the [upstream scope](https://github.com/OpenAI/math/blob/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb/lean/docs/130.md).

The comparator challenge ends in deliberate `sorry` placeholders. Its named
solution is the separate Main module, not those placeholders. The [recorded
comparison configuration](snapshot/source/lean/ComparatorChallenges/UniformFourier.json)
names the two main theorems and permitted axioms; the optional Nanoda setting is
false. No local axiom or theorem admission is inferred from source inspection.

## Contents and validation

- [Snapshot source manifest](snapshot/source-manifest.json): 97 exact public
  source/configuration files, 645,234 bytes, with original URLs and hashes.
- [Storage mapping](snapshot-storage.json): 104 preserved snapshot files,
  including the original notes and manifest. Raw upstream Markdown is stored as
  `.md.txt` so incomplete upstream relative-link trees are not presented as local
  documentation. Contents are unchanged; no target stubs were fabricated.
- [Offline receipt](receipt.json): full source/storage pins, 89-module local
  proof import closure, normalized RAM match and 16 normalized goal/time
  definition matches. The prior [static receipt](snapshot/static-source-checks.json)
  is independently recomputed by the packet verifier, not merely repeated as prose.
- [Upstream license](UPSTREAM_LICENSE), [attribution notice](NOTICE) and
  [provenance](provenance.json): exact Apache-2.0 license and captured root listing.
- [Prospective declaration commands](snapshot/AuditUniformFourier.lean): not
  compiled. Historical staging notes inside `snapshot/` are preserved unchanged;
  this README and the packet receipt state the current verification boundary.

From this directory, run:

```sh
python3 -I -B verify.py --check
python3 -I -B -O verify.py --check
```

The verifier is stdlib-only and offline. It never imports or executes the captured
Lean/Lake source, the preserved fetch script, or any downloaded package. Eleven
refusal controls and three positive controls exercise hashes, strict lengths,
paths, missing/unsupported imports, lexical parsing, changed propositions and
typed receipt comparisons. Lexical checks are not a Lean parser or a transitive
axiom audit. The unchanged source fetch script is historical evidence and is
not a replay dependency.

## Next bounded step

Audit the two target declarations in an isolated, pinned Lean `v4.34.1` and
Mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612` environment. First account for
toolchain and transitive dependency availability. Preserve source bytes, compile
only Main and its actual dependencies, inspect/export its theorem types and
axiom dependencies, and run the configured comparator with recorded tool
versions in separate challenge/solution environments.

The captured repository-wide [Lake file](snapshot/source/lean/lakefile.lean)
has configuration-time dependency clone/patch hooks; invoking it is not a
read-only source query. No such invocation or dependency acquisition occurs in
this packet. A future declaration check would establish only the selected formal
statements in their declared arithmetic model, without numerical-stability,
bit-complexity, synthesis-appendix, novelty or practical-speedup claims.
