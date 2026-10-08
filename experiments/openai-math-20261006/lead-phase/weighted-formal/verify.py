#!/usr/bin/env python3
"""Rebuild pinned local Lean algebra; reject three false strengthenings.

Default replay is read-only except for ignored .build files. --record explicitly
records a new receipt and compiler logs. No external proof configuration runs.
"""

import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT.parent.parent
DEPENDENCIES = {
    "research-sprint/density-transport/CubicStrip.lean":
        "2aeb918e00adf8526ae56020894523ea041a2967253c058c2799c8b27b00a732",
    "research-next/formal-bridge/FormalBridge.lean":
        "2f33eba79f926020d7482d2782de45b5621857714ea1e7c7cdc2f4837f043b59",
}
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
NEGATIVE_FILES = ["OmitDefect.lean", "OmitThreshold.lean", "OmitParity.lean"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite_checks():
    """Arithmetic implementation controls; the Lean theorems are unbounded."""
    squares = 0
    for A in range(1, 13):
        for d in range(4*A, 4*A + 31):
            for n in range(-50, 101):
                F = (n-1)*(n-2) - A*d*(3*n-d*d-2)
                rhs = ((2*n-3*A*d-3)**2 + 4*A*d*d*(d-4*A)
                       + 7*(A*d-4)**2 + 46*(A*d-4) + 71)
                assert 4*F == rhs and F > 0
                squares += 1

    quotients = 0
    restoration = 0
    smallest_weighted = None
    strictly_weighted = 0
    for n in range(8, 401, 4):
        P = (n-1)*(n-2)
        for j in range(1, n//2):
            g = math.gcd(n, j)
            u, v, d = j//g, n//g, n-2*j
            Q = u*(v-u)*(v-2*u)
            assert Q > 0 and Q % 2 == 0
            assert 4*g**3*Q == d*(n*n-d*d)
            for A in range(1, min(d//4, 20)+1):
                if A*Q % P:
                    continue
                k = A*Q//P
                m = 4*g**3*k-A*d
                assert k >= 1 and m <= -2 and m % 2 == 0
                assert m*P == A*d*(3*n-d*d-2)
                assert A*d**3 >= 2*n*n + (A*d-2)*(3*n-2) > 2*n*n
                assert A*d > 4*g**3
                if d % 4 == 0:
                    assert m % 4 == 0
                    assert A*d**3 >= 4*n*n + (A*d-4)*(3*n-2)
                quotients += 1
                if Q % P:
                    strictly_weighted += 1
                    if smallest_weighted is None:
                        smallest_weighted = {"n": n, "j": j, "A": A, "g": g,
                                             "d": d, "Q": Q, "P": P, "k": k, "m": m}
            # Explicit product inputs exercise restoration separately from the strip.
            for B in range(1, 26, 2):
                if (n-1) % B or u*(v-u) % B:
                    continue
                for C in range(1, 26, 2):
                    if ((n-2)//2) % C or (4*Q) % C or math.gcd(B, C) != 1:
                        continue
                    assert P % (2*B*C) == 0
                    A = P//(2*B*C)
                    assert A*Q % P == 0
                    restoration += 1
    assert quotients > 0 and restoration > 0 and smallest_weighted is not None

    n, j, A, B, C, k = 16, 7, 15, 1, 7, 9
    d, g, u, v = n-2*j, math.gcd(n, j), 7, 16
    Q, P = u*(v-u)*(v-2*u), (n-1)*(n-2)
    m = 4*g**3*k-A*d
    assert P == 2*A*B*C and math.gcd(B, C) == math.gcd(C, 4) == math.gcd(2, B*C) == 1
    assert u*(v-u) % B == (4*Q) % C == 0
    assert (n-2) % C == 0 and j % C <= 2
    assert Q == 126 and P == 210 and A*Q == k*P
    assert Q % P != 0 and m == 6 and d < 4*A
    assert m*P == A*d*(3*n-d*d-2)
    assert 0*((6-1)*(6-2)) == 1*4*(3*6-4*4-2)
    assert not 2*6*6 < 1*4**3
    return {
        "obstruction_grid": {"A": [1, 12], "d": "4A through 4A+30",
                             "n": [-50, 100], "count": squares},
        "normalized_rows": {"n": "multiples of 4 from 8 through 400",
                            "j": "1 <= j < n/2", "A": "1 through min(d//4,20)",
                            "weighted_divisor_passes": quotients,
                            "passes_where_P_does_not_divide_Q": strictly_weighted,
                            "first_pass_where_P_does_not_divide_Q": smallest_weighted},
        "restoration_grid": {"B_C": "odd divisors from 1 through 25",
                             "passing_product_data": restoration},
        "exact_controls": {"defect_and_threshold": {"n": n, "j": j, "A": A, "B": B,
                                                    "C": C, "Q": Q, "P": P, "k": k, "m": m},
                           "zero_quotient": {"n": 6, "d": 4, "A": 1, "m": 0}},
    }


def comparable(receipt):
    """Binary digests are diagnostic; proof-source and verdict data are portable."""
    return {key: receipt[key] for key in ["schema", "graph_nodes", "scope", "not_formalized",
            "external_openai_proofs_rebuilt", "canonical_status_changed", "sources",
            "verifier_sha256", "axiom_audit", "negative_controls", "optimized_python_rejected",
            "finite_checks"]}


def main():
    if not __debug__:
        raise SystemExit("Refusing optimized Python: verification assertions must remain enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", required=True, help="Lean 4.33.1 executable")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    lean = str(Path(args.lean).resolve())
    optimized = subprocess.run([sys.executable, "-O", "-I", str(Path(__file__).resolve()),
                                "--lean", lean], text=True, capture_output=True)
    assert optimized.returncode != 0 and "Refusing optimized Python" in optimized.stderr
    version = subprocess.run([lean, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    assert version.startswith("Lean (version 4.33.1,"), version
    for name, expected in DEPENDENCIES.items():
        assert digest(BUNDLE / name) == expected, f"Dependency changed: {name}"

    source = ROOT / "WeightedFormal.lean"
    sources = [BUNDLE / name for name in DEPENDENCIES] + [source]
    for path in sources:
        assert not re.search(r"\b(sorry|admit|axiom)\b", path.read_text()), path
    theorem_names = re.findall(r"^theorem (\w+)", source.read_text(), re.MULTILINE)
    printed_names = re.findall(r"^#print axioms (\w+)", source.read_text(), re.MULTILINE)
    assert theorem_names == printed_names and len(theorem_names) == 15

    build = ROOT / ".build"
    build.mkdir(exist_ok=True)
    env = dict(os.environ, LEAN_PATH=str(build))
    builds, logs = [], []
    for path in sources:
        output_path = build / f"{path.stem}.olean"
        argv = ["-o", os.path.relpath(output_path, path.parent), path.name]
        result = subprocess.run([lean, *argv], cwd=path.parent, env=env, text=True, capture_output=True)
        output = result.stdout + result.stderr
        if result.returncode:
            print(output)
            raise SystemExit(result.returncode)
        assert "sorryAx" not in output and "warning:" not in output, output
        logs.append(output)
        builds.append({"source": path.relative_to(BUNDLE).as_posix(),
                       "cwd": path.parent.relative_to(BUNDLE).as_posix(),
                       "command": ["<lean>", *argv], "exit_code": result.returncode,
                       "olean_sha256": digest(output_path)})

    audits = {}
    for name in theorem_names:
        full_name = f"WeightedFormal.{name}"
        match = re.search(r"'" + re.escape(full_name) + r"' depends on axioms: \[([^\]]*)\]", logs[-1])
        if match:
            axioms = [a.strip() for a in match[1].split(",") if a.strip()]
        else:
            assert f"'{full_name}' does not depend on any axioms" in logs[-1]
            axioms = []
        assert set(axioms) <= ALLOWED_AXIOMS, (name, axioms)
        audits[name] = axioms

    controls, control_logs = [], []
    for filename in NEGATIVE_FILES:
        relative = f"negative/{filename}"
        result = subprocess.run([lean, relative], cwd=ROOT, env=env, text=True, capture_output=True)
        output = result.stdout + result.stderr
        assert result.returncode != 0 and "proved that the proposition" in output and "false" in output, output
        assert "unknown module" not in output.lower() and "object file" not in output.lower(), output
        controls.append({"source": relative, "source_sha256": digest(ROOT / relative),
                         "expected_rejection": True, "exit_code": result.returncode})
        control_logs.append(relative + "\n" + output)

    receipt = {
        "schema": "efa-weighted-positional-bridge-v1",
        "verified_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "graph_nodes": ["P699", "S:triage:699"],
        "scope": "explicit finite positional blocks to weighted divisor, positive quotient, coefficient-two and coefficient-four cubic bounds, and gcd gap",
        "not_formalized": ["binomial valuation localization", "prime-power extraction from P699 failure",
                           "construction of the small-prime factor A and its block decomposition",
                           "defect-free boundary cases d=0 and d=2", "full P699"],
        "external_openai_proofs_rebuilt": False,
        "canonical_status_changed": False,
        "sources": {path.relative_to(BUNDLE).as_posix(): digest(path) for path in sources},
        "verifier_sha256": digest(__file__),
        "toolchain_version": version, "lean_executable_sha256": digest(lean),
        "path_convention": "cwd and sources relative to bundle; command file arguments relative to cwd; <lean> is the supplied executable",
        "builds": builds, "axiom_audit": audits, "negative_controls": controls,
        "optimized_python_rejected": True,
        "finite_checks": finite_checks(),
    }
    receipt_path = ROOT / "execution.json"
    if args.record:
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
        (ROOT / "axiom-audit.log").write_text("\n".join(logs))
        (ROOT / "negative-controls.log").write_text("\n".join(control_logs))
    else:
        recorded = json.loads(receipt_path.read_text())
        assert comparable(recorded) == comparable(receipt), "Recorded evidence differs; inspect before recording a replacement"
    print(json.dumps({"result": "PASS", "audited_theorems": len(audits),
                      "negative_controls_rejected": len(controls),
                      "weighted_divisor_finite_passes": receipt["finite_checks"]["normalized_rows"]["weighted_divisor_passes"],
                      "source_sha256": digest(source)}))


if __name__ == "__main__":
    main()
