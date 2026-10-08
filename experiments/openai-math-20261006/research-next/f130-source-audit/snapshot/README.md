# F130 pure-mathematics staging

This packet contains only public primary-source mathematics and a source-level audit proposal. It has not been admitted into a public candidate repository.

- [F130_SCOPE.md](F130_SCOPE.md): quantified statements, exact-arithmetic model, supplied-root premise, exclusions and one proposed declaration-level audit.
- [source-manifest.json](source-manifest.json): exact URLs, SHA-256 values and imports for 97 files at OpenAI/math commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` (645,234 bytes).
- [static-source-checks.json](static-source-checks.json): bounded textual checks; explicitly not a Lean proof check.
- [AuditUniformFourier.lean](AuditUniformFourier.lean): prospective declaration/axiom print commands, not compiled.
- [fetch_sources.py](fetch_sources.py): the bounded public-source fetch used for this packet. It refuses overwrite and fetches no dependency packages, caches or executables.

No Lake command, Lean build, comparator, declaration export, synthesis extraction or benchmark was run. The repository-wide Lake configuration contains dependency clone/patch hooks; the next audit should first prepare a separately pinned, isolated environment. Successful future verification would apply to the exact selected mathematical declarations and their formal model, not to practical running time, numerical stability or the omitted synthesis appendix.
