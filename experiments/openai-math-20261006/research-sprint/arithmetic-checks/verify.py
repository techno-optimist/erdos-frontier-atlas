#!/usr/bin/env python3
"""Replay the local algebraic Lean proof; its arithmetic reduction remains informal."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
NAMES = ['seven_diagonal_positive', 'seven_diagonal_no_weak_bound', 'seven_diagonal_no_gcd_bound']

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lean', required=True)
    p.add_argument('--record', action='store_true')
    args = p.parse_args()
    lean = str(Path(args.lean).resolve())
    version = subprocess.check_output([lean, '--version'], text=True).strip()
    assert version.startswith('Lean (version 4.33.1,'), version
    source = HERE / 'DiagonalInequality.lean'
    assert not re.search(r'\b(sorry|admit|axiom)\b', source.read_text())
    r = subprocess.run([lean, source.name], cwd=HERE, capture_output=True, text=True)
    output = r.stdout + r.stderr
    assert r.returncode == 0, output
    axioms = {}
    for name in NAMES:
        m = re.search(r"'DiagonalInequality\." + name + r"' depends on axioms: \[([^\]]*)\]", output)
        assert m, output
        found = [s.strip() for s in m[1].split(',') if s.strip()]
        assert set(found) <= {'propext', 'Quot.sound', 'Classical.choice'}, found
        axioms[name] = found
    negative = subprocess.run([lean, 'negative/ExtendTo32.lean'], cwd=HERE, capture_output=True, text=True)
    negative_output = negative.stdout + negative.stderr
    assert negative.returncode != 0 and 'Tactic `decide` proved' in negative_output and 'is false' in negative_output, negative_output
    digest = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
    data = {'schema': 'efa-seven-diagonal-algebra-lean-v1', 'problem_id': 'P699', 'surface_id': 'S:triage:699',
            'scope': 'Three algebraic implications only; prime-power localization, divisibility restoration and full P699 reduction are not formalized here.',
            'toolchain': version, 'source_sha256': digest(source), 'verifier_sha256': digest(__file__),
            'lean_executable_sha256': digest(lean), 'compile_exit_code': r.returncode,
            'axioms': axioms, 'negative_control_rejected': True,
            'negative_source_sha256': digest(HERE / 'negative/ExtendTo32.lean')}
    if args.record:
        (HERE / 'execution.json').write_text(json.dumps(data, indent=2) + '\n')
        (HERE / 'axiom-audit.log').write_text(output)
        (HERE / 'negative-control.log').write_text(negative_output)
    print('PASS: three algebraic theorems; standard axioms only; false d=32 extension rejected.')

if __name__ == '__main__':
    main()
