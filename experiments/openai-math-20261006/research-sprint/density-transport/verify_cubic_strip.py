#!/usr/bin/env python3
"""Compile the explicitly scoped integer algebra and audit kernel dependencies."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
NAMES = ['obstruction_identity', 'obstruction_positive', 'quotient_negative',
         'growing_strip', 'quotient_bound', 'parity_nonzero',
         'even_quotient_strip', 'four_quotient_strip', 'gcd_gap',
         'zero_quotient_control']
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    lean = str(Path(args.lean).resolve())
    version = subprocess.run([lean, '--version'], text=True, capture_output=True, check=True).stdout.strip()
    assert version.startswith('Lean (version 4.33.1,'), version
    source = ROOT / 'CubicStrip.lean'
    assert not re.search(r'\b(sorry|admit|axiom)\b', source.read_text())
    build = ROOT / '.build'
    build.mkdir(exist_ok=True)
    command = [lean, '-o', '.build/CubicStrip.olean', 'CubicStrip.lean']
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    if result.returncode:
        print(output)
        raise SystemExit(result.returncode)
    assert 'sorryAx' not in output
    audits = {}
    for name in NAMES:
        match = re.search(r"'CubicStrip\." + name + r"' depends on axioms: \[([^\]]*)\]", output)
        if match:
            axioms = [x.strip() for x in match.group(1).split(',') if x.strip()]
        else:
            assert f"'CubicStrip.{name}' does not depend on any axioms" in output, output
            axioms = []
        assert set(axioms) <= ALLOWED, (name, axioms)
        audits[name] = axioms
    receipt = {
        'schema': 'efa-cubic-strip-lean-receipt-v1',
        'verified_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'verification_scope': 'integer polynomial and explicit quotient-hypothesis implications only; no Kummer or P699 arithmetic reduction formalized',
        'external_openai_proofs_rebuilt': False,
        'toolchain_version': version,
        'lean_executable': lean,
        'lean_executable_sha256': digest(lean),
        'compile_command': command,
        'compile_exit_code': result.returncode,
        'source_sha256': digest(source),
        'verifier_sha256': digest(__file__),
        'proof_olean_sha256': digest(build / 'CubicStrip.olean'),
        'axiom_audit': audits,
        'countermodel': {'theorem': 'zero_quotient_control', 'n': 6, 'd': 4, 'm': 0,
                        'purpose': 'nonzero premise cannot be omitted from general quotient theorem'},
    }
    if args.record:
        (ROOT / 'cubic-strip-execution.json').write_text(json.dumps(receipt, indent=2) + '\n')
        (ROOT / 'cubic-strip-axiom-audit.log').write_text(output)
    print(json.dumps({'result': 'PASS', 'audited_theorems': len(audits), 'source_sha256': digest(source)}))

if __name__ == '__main__':
    main()
