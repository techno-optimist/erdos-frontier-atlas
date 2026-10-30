#!/usr/bin/env python3
"""Replay the two recovered Erdos #142 no-go certificates (stdlib only).

1. Universal additive piece-local potential no-go (4-term exact Farkas).
2. Order-two pair-context affine lift no-go (2767-term exact Farkas).
Both run against the same pinned geometry as certificates/erdos-142.
Exit 0 iff both verify.  Not an r_3(N) bound.
"""
import hashlib, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {
    "complete_sos/artifacts/full_vertex_farkas_exact_4term.json":
        "451fea0d12e2c7a9e613d4426450bd83baf3eb737be9e6c4bf94ca9be6261d8c",
    "complete_sos/artifacts/context_pair_affine_farkas_exact_2767term_flintbasis.json":
        "ed0e6c903c5b0f338490da95cfc2a505de62132ff0e9a90adfd85a8f6282a926",
    "complete_enum/geometry.json":
        "607841330978360a10b3440598a034f6ade903b8afe872c1cbe7bdf441e92ada",
}
for rel, h in PINS.items():
    got = hashlib.sha256((HERE / rel).read_bytes()).hexdigest()
    if got != h:
        sys.exit(f"FAIL: sha256 mismatch for {rel}: {got}")
geo = str(HERE / "complete_enum/geometry.json")
cells = str(HERE / "complete_enum/out/fulldim_cells_canonical.json")
runs = [
    ([str(HERE / "complete_sos/verify_universal_local_nogo.py"),
      str(HERE / "complete_sos/artifacts/full_vertex_farkas_exact_4term.json"), geo, "--anchors", cells],
     "UNIVERSAL LOCAL-POTENTIAL NO-GO VERIFIER PASS"),
    ([str(HERE / "complete_sos/verify_context_pair_affine_farkas.py"),
      str(HERE / "complete_sos/artifacts/context_pair_affine_farkas_exact_2767term_flintbasis.json"), geo, cells],
     "ORDER-TWO PAIR-AFFINE FARKAS VERIFIER PASS"),
]
for argv, marker in runs:
    p = subprocess.run([sys.executable, "-S"] + argv, capture_output=True, text=True)
    sys.stdout.write(p.stdout)
    if p.returncode != 0 or marker not in p.stdout:
        sys.stderr.write(p.stderr)
        sys.exit("FAIL: " + Path(argv[0]).name)
print("RESULT: BOTH NO-GO CERTIFICATES VALID (pins 451fea0d..., ed0e6c90...); NOT an r_3(N) bound")
