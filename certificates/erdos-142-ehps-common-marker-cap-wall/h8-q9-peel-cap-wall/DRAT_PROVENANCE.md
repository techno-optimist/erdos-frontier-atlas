# External DRAT provenance and compression trial

The combined theorem does not depend on DRAT: `compact_fibre_verify.cpp`
gives a direct finite exhaustive proof for both conditional masters.  The raw
proofs remain in their frozen source packets as independent provenance and are
not copied into this promotion-size package.

Both traces were emitted by official CaDiCaL 3.0.1, commit
`c60730422e758ef1cebe7aeddf2dda31c996bf04`, in non-binary DRAT format.  Both
were checked by independently compiled Windows and Linux builds of official
`drat-trim`, commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`.

| Proof | Raw bytes | Raw SHA-256 | drat-trim result |
|---|---:|---|---|
| template0 | 328,976,151 | `9291e1af32323c1122760e286ff945866f54f66ff321db04e8524fbbe000a1a3` | `s VERIFIED`; 1,992,430/3,127,782 core lemmas; 67,593,243 resolution steps |
| template1 | 238,241,255 | `e1fc93a8ece1da8fc2d3a7cef3a8f9a11ecca79460ebcba190b6ee4ee3f05d3f` | `s VERIFIED`; 1,541,852/2,279,938 core lemmas; 49,355,215 resolution steps |

Deterministic compression was tested on the exact raw files.  `gzip` used
`gzip -n -9`; zstd used CLI 1.5.6 with `-T0` at levels 19 and ultra 22.

| Proof | Encoding | Bytes | Raw ratio | SHA-256 | Compression seconds |
|---|---|---:|---:|---|---:|
| template0 | gzip-9 | 67,770,522 | 20.600% | `e2e331c7e595fef1c758d1d314f15feaf81a9938d8d46c6633929538f74cd03a` | 51.50 |
| template0 | zstd-19 | 58,762,411 | 17.862% | `aa4cb382908ea2e62fbe355ed17311e9dd3055196cbcbbe22f2db94fb06c4e57` | 28.76 |
| template0 | zstd-22 | 58,517,639 | 17.788% | `e5be8f08f3b7c0168fdb80279aeb4978b0c79601c84a2ab2e9624d306a77a4dc` | 249.40 |
| template1 | gzip-9 | 49,368,356 | 20.722% | `ebceda8778fa037fb222f3b946b2a4b0c2d5c6843f9dbcc967eba324f44d57aa` | 38.94 |
| template1 | zstd-19 | 42,809,957 | 17.969% | `936e129691ac2828b01e12ebbbfce16bcf12283f2c21cc91e3bf8f657c5e19d7` | 28.71 |
| template1 | zstd-22 | 42,639,205 | 17.897% | `9bc0719196cb7295f6ccbea1049780cc3064b3049b9d66fb7e884f2445c4485a` | 183.08 |

All six deterministic artifacts were regenerated from the frozen raw traces,
matched the listed compressed size and SHA-256, and were then decompressed.
Each expansion matched its listed raw SHA-256 byte for byte.

The raw pair totals 567,217,406 bytes; gzip-9 totals 117,138,878 bytes;
zstd-19 totals 101,572,368 bytes; and zstd-22 totals 101,156,844 bytes.
Under GitHub's documented regular-Git policy as checked on 2026-08-19, the
100 MiB block is per file, not per pair.  Thus each compressed artifact is
technically below the hard block, although all three template0 encodings are
above the 50 MiB warning threshold.  Each raw proof individually exceeds the
100 MiB block.  Even the smallest compressed pair costs over 101 MB in
aggregate, adds no theorem strength beyond the direct source-level DFS, and
would burden every clone.  Therefore no proof payload or compiled
`drat-trim` binary is included here; a release asset or external archive is
the appropriate lane for the independent traces.  The policy reference is
<https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github>.

The experimental `drat-trim -l ... -C` binary-core route is explicitly not
used: its emitted artifact failed an independent recheck with malformed and
deletion warnings.  No theorem claim relies on that failed experiment.
