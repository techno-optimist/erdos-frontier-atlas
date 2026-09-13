# P327 source check — 2026-09-12

**Separate the catalog, mathematical papers, and submitted proof claims.** No official problem status is changed by this bundle.

| Register | Observation |
|---|---|
| Live official problem page | Banner OPEN; 11 comments, 2 proof claims, 0 proof expositions.[1] |
| Community YAML | At `3c68e941162f81d650fc886eed34e58bed3a6a01` (commit 2026-09-09), record 327 has informal status `open` and formal status `unformalized`. This is the same upstream pin as the previous freshness overlay.[12] |
| Discussion | Yu Leon Liu reports bounds 0.7769 for k=1 and 0.7630 for k=2 using P={2,3,5,7,11,13}, cutoff 2000; the current linked paper contains the smooth–rough theorem and the computation link.[4][8] |
| Partial result | Will Sawin's arXiv:2607.15419 states a positive-density construction for the k=2 variant, answering that part negatively. The proof register lists it as partial, with review comments. Its theorem and construction were read for scope; the analytic proof was not independently audited here.[5][9] |
| Full submission | The register separately lists Donald Della Pietra's full proof/formalization claim, submitted 2026-07-29. Its correctness and Lean build were **not** audited here, and it does not override the observed OPEN banner.[5] |

This prevents treating the second question as untouched simply because the aggregate banner is OPEN. Conversely, the existence of a full submission is not official acceptance or independent verification.

## Relationship to Liu's method

The modulus-1 specialization of our theorem is Liu's Theorem 19 expressed as a sum of prefix deficiencies. The extra ingredient investigated here is conditioning on `gcd(m,L)` so that additional forbidden pairs become available within a fiber.[8]

The demonstration deliberately uses a tiny, unchanged smooth prefix; **317/360 is not a new best density bound**. No replay of Liu's 2000-cutoff numerical constants was performed.[8]

The linked `erdos327_cert.py` retrieved for context uses a time-limited MILP incumbent as its prefix value without checking the solve status in that code path. This observation does **not** invalidate the reported numbers or the mathematical theorem. It means that script alone is not our independent optimality certificate; the present small examples instead use exhaustive subset checks and rational arithmetic.[10]

## Retrieval and licensing

The generic extractor initially returned an older version of the official page without its current discussion material; the browser's live page, discussion, and expanded proof comments supplied the snapshot above.[1][4][5] The old `erdos327.pdf` URL returned an HTML redirect with HTTP 200. The canonical PDF URL was followed and its actual bytes hashed.[8]

`sources.json` records URLs, pins, and SHA-256 digests. Downloaded third-party manuscripts and raw site text remain outside the repository. Only independently written mathematical exposition and source metadata are included here.

## Sources

[1] https://www.erdosproblems.com/327
[4] https://www.erdosproblems.com/forum/discuss/327
[5] https://www.erdosproblems.com/forum/thread/327/proof-claims
[8] https://leon2k2k2k.github.io/assets/pdf/erdos/erdos327.pdf
[9] https://arxiv.org/abs/2607.15419
[10] https://github.com/leon2k2k2k/leon2k2k2k.github.io/blob/master/erdos327_cert.py
[12] https://github.com/teorth/erdosproblems/blob/3c68e941162f81d650fc886eed34e58bed3a6a01/data/problems.yaml
