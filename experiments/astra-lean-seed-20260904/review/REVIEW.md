# Independent Lean seed review

**Verdict: PASS for the stated algebraic seed and its axiom gate. No blocking issues found.**

## Scope and exact statements

Reviewed source snapshot: `experiments/astra-lean-seed-20260904/`. Source filenames below are relative to that project directory; review artifacts are relative to this report. `source-sha256.json` records the reviewed bytes, and `results.json` confirms those source files remained byte-identical throughout the final run. No original source or proof-build artifacts were edited. Compilation outputs were confined to the separate review workspace.

The main theorem is exactly:

```lean
∀ j k : Nat,
  (k + 1) * Nat.gcd (Nat.choose j k) (Nat.choose (j + 1) (k + 1)) =
    Nat.choose j k * Nat.gcd (k + 1) (j + 1)
```

`AdjacentBinomialGcd.lean:17–25` proves this with no hypotheses. In particular, there is no `k ≤ j`, positivity assumption, or hidden section parameter. `ExactStatement.lean:6–9` independently assigns the named theorem to this universal type and compiled successfully. The ordinary `Nat.choose` convention applies outside the lower-index range.

The optional theorem is exactly:

```lean
∀ U A B C j : Nat,
  U ∣ B → Nat.gcd U A = 1 → A * C = (j + 1) * B → U ∣ C
```

`AdjacentBinomialGcd.lean:28–35` and the independent contract in `DivisorTransferCheck.lean:6–8` agree. There are precisely the displayed hypotheses; the variables need not themselves be binomial coefficients.

## Arithmetic and proof audit

- The source contains no custom axiom declaration, `sorry`, `admit`, or `native_decide`. The concrete witness checks and altered-identity negative control use ordinary `decide`.
- No shadowing definitions, custom arithmetic instances, or local arithmetic notation occur in the reviewed source.
- The independent `FullyQualified.lean` check compiled both contracts using root-qualified `Nat`, `Eq`, `Nat.add`, `Nat.mul`, `Nat.choose`, and `Nat.gcd`; divisibility was explicitly instantiated as `Dvd.dvd Nat Nat.instDvd`. The expanded types in `FullyQualified.log` show the standard natural addition, multiplication, numeral, and divisibility instances, with no extra parameters.
- The homogeneous gcd lemma uses `Nat.gcd_mul_left`, rewriting, and commutativity. The binomial specialization discharges its product relation using `Nat.add_one_mul_choose_eq`. No cancellation or division step introduces an unstated nonzero assumption.
- The divisor-transfer proof first derives `U ∣ A * C` and then removes the coprime factor using standard gcd lemmas.
- Actual `#print axioms` output for each of the three named theorems is exactly `[propext, Quot.sound]`. Neither `Classical.choice`, `sorryAx`, nor a custom axiom appears in these transitive dependency reports. This is an audit of theorem dependencies, not a claim that the entire imported library declares no other axioms.

## Actual execution

Toolchain reported Lean **4.33.1**, compiler commit `819816b2e0a3bf405af45ae5c7af2491d8f5bee6`. The dependency checkout reported Mathlib commit `0df444a360eaa60ab8c11dca51a86af692955474`.

The reviewer obtained dependency search paths through the original scratch project's `lake env printenv LEAN_PATH`, prepended the isolated review directory, and invoked the supplied Lean binary directly on copied source. `AdjacentBinomialGcd.olean` was rebuilt in that isolated directory before importing it into the checks; this did not rely on an old compiled copy of the seed theorem.

| Module | Lean exit | Interpretation |
| --- | ---: | --- |
| `AdjacentBinomialGcd.lean` | 0 | Fresh isolated proof compilation |
| `ExactStatement.lean` | 0 | Exact universal identity accepted |
| `DivisorTransferCheck.lean` | 0 | Exact optional contract accepted |
| `AxiomAudit.lean` | 0 | All original standard-axiom guards accepted |
| `LibraryChecks.lean` | 0 | Library signatures, proof terms, concrete witnesses checked |
| `FullyQualified.lean` | 0 | Root-qualified independent contracts accepted |
| `PoisonedGuard.lean` | 1 | Required axiom-contamination rejection |
| `negative/AlteredIdentity.lean` | 1 | Ordinary `decide` rejected the false alteration |

### Axiom-gate negative control

The isolated `PoisonedGuard.lean` declares `ReviewPoison.poison (n : Nat) : n = n` as a **custom axiom**, and explicitly uses it via `Eq.trans` in a proof of the same binomial identity. Its `#guard_msgs` expects only the same standard axiom list as the original audit. Lean exited **1**, with exactly one error, caused by that list mismatch:

```text
PoisonedGuard.lean:15:0: error: ❌️ Docstring on `#guard_msgs` does not match generated message:

- info: 'ReviewPoison.poisoned_adjacent_binomial_gcd' depends on axioms: [propext, Quot.sound]
+ info: 'ReviewPoison.poisoned_adjacent_binomial_gcd' depends on axioms: [propext, Quot.sound, poison]
```

Imports and the poisoned proof elaborated; this was not a missing-import failure. The custom axiom is reflexivity-shaped but intentionally forbidden by the allowlist: contamination need not be inconsistent to be rejected. See `PoisonedGuard.log`.

The separate altered-identity control also exited 1, explicitly reporting that `decide` proved the displayed proposition false. See `negative_AlteredIdentity.log`.

## Dependency configuration

`lakefile.toml:5–8` uses the public Mathlib Git URL and the full revision `0df444a360eaa60ab8c11dca51a86af692955474`, not a local path or moving branch. `lean-toolchain` pins `leanprover/lean4:v4.33.1`. The default targets include the main library, both separate exact-statement modules, the axiom audit, and library checks; the deliberately false module is excluded.

## Limitations and reviewer-harness corrections

- This review did not run a clean network dependency installation or rebuild the parent's packaged project. Portable dependency resolution, its eventual manifest, and the parent's full build remain separate verification obligations.
- Existing dependency build artifacts and the supplied Lean toolchain were trusted; Mathlib and Lean were not independently rebuilt or supply-chain audited.
- The review covers this source snapshot and small algebraic statements only. EEES, prime-power localization, the broader Erdős problem, novelty, and upstream acceptance are not established. Those unformalized ingredients are not assumptions of these Lean theorems.
- The axiom gate detects changed theorem dependencies while the expected guard remains intact. It is not protection against someone deliberately editing the theorem and its expected audit together, or against arbitrary compromised tooling.
- Initial reviewer-only harness issues were corrected before the final successful run: natural divisibility uses `Nat.instDvd` rather than a nonexistent `Nat.dvd` constant; guard-output matching was adjusted to Lean's actual shortened `poison` name and `does not match generated message` wording. Neither correction touched the reviewed project. The table and saved logs describe the final rerun.

All displayed paths are project-relative or review-artifact-relative; no machine-specific absolute paths are included in this report.
