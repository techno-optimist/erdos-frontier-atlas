# Reading / replay guide

Start with `audit.md`. It contains the mathematical deduction, a sourced parameter ledger, epsilon margins, and the surviving bottleneck. The result is a proof-transfer audit, not a priority claim or an RH proof.

Replay the exact parameter arithmetic (Python standard library only):

```sh
python3 check_exponents.py
```

This regenerates `exponent-results.json`. It verifies the old 6/11 ceiling, the direct GM 4/7 ceiling, the refined Proposition 12.1 critical-level ceiling, coefficient normalization, positive epsilon margins, and a just-beyond-ceiling negative control.

Evidence files:

- `source-excerpts.md`: verbatim formula-preserving blocks.
- `source-locators.json`: source URLs are identified by the accompanying `citations.json`; includes equation/page/source-line locators.
- `primary-manifest.json`: byte sizes and SHA-256 of primary copies.
- `pdf-manifest.json`: complete PDF page counts, extraction counts and metadata.
- `gmrr-source/squfv.tex`, `gm-source/LargevaluesDirichlet17.tex`: complete primary TeX, used to resolve PDF formula layout.
- `gm-v2.html.math.txt`: HTML text with MathML alttext substituted in place of rendered math.
- `gm-main-theorem-v1-v2-comparison.json`: byte-identical Theorem 1.1 source blocks across arXiv versions.
- `exponent-execution.log`: real exact-arithmetic run output.

The Annals DOI target was an Incapsula interstitial; `gm-doi-response` is preserved only as failed-retrieval evidence, not used as article content. The arXiv replacement theorem was inspected in full TeX and PDF and checked against both v1 and v2.

`extract_primary.py`, `extract_html_math.py`, and `build_evidence.py` record the reading-copy and evidence procedures. Re-extraction uses pypdf and fonttools (the audit used an isolated uv environment). The arithmetic checker does not require them. All research artifacts here are separate from any repository, staging area, or proof-production gate.
