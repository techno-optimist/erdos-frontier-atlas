#!/usr/bin/env python3
"""Rebuild the positional bridge and its owned dependency, audit axioms, reject false controls."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT.parent.parent
DEPENDENCY = BUNDLE / 'research-sprint/density-transport/CubicStrip.lean'
EXPECTED_DEPENDENCY = '2aeb918e00adf8526ae56020894523ea041a2967253c058c2799c8b27b00a732'
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
NAMES = ['cancel_coprime', 'coprime_product', 'q_even', 'q_three', 'restore_cubic',
         'local_linear', 'position_one', 'position_two', 'localAt_of_residues', 'blocks_product_dvd',
         'positional_products', 'quotient_from_cubic', 'strip_from_cubic',
         'strip_from_positional_products', 'strip_from_blocks', 'strip_from_blocks_two']

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
    assert digest(DEPENDENCY) == EXPECTED_DEPENDENCY, 'imported source changed: inspect before repinning'
    source = ROOT / 'FormalBridge.lean'
    for path in [source, DEPENDENCY]:
        assert not re.search(r'\b(sorry|admit|axiom)\b', path.read_text()), path
    build = ROOT / '.build'
    build.mkdir(exist_ok=True)
    env = dict(os.environ)
    env['LEAN_PATH'] = str(build)
    builds = []
    logs = []
    for path in [DEPENDENCY, source]:
        command = [lean, '-o', os.path.relpath(build / (path.stem + '.olean'), path.parent), path.name]
        result = subprocess.run(command, cwd=path.parent, env=env, text=True, capture_output=True)
        output = result.stdout + result.stderr
        if result.returncode:
            print(output)
            raise SystemExit(result.returncode)
        assert 'sorryAx' not in output and 'warning:' not in output, output
        logs.append(output)
        builds.append({'source': str(path.relative_to(BUNDLE)),
                       'source_sha256': digest(path), 'command': command,
                       'exit_code': result.returncode, 'cwd': str(path.parent.relative_to(BUNDLE)),
                       'olean_sha256': digest(build / (path.stem + '.olean'))})
    audits = {}
    for name in NAMES:
        match = re.search(r"'FormalBridge\." + name + r"' depends on axioms: \[([^\]]*)\]", logs[-1])
        if match:
            axioms = [x.strip() for x in match.group(1).split(',') if x.strip()]
        else:
            assert f"'FormalBridge.{name}' does not depend on any axioms" in logs[-1]
            axioms = []
        assert set(axioms) <= ALLOWED, (name, axioms)
        audits[name] = axioms
    controls, control_logs = [], []
    for filename in ['negative/OmitCoprimality.lean', 'negative/OmitThreeCondition.lean']:
        result = subprocess.run([lean, filename], cwd=ROOT, env=env, text=True, capture_output=True)
        output = result.stdout + result.stderr
        assert result.returncode != 0, filename
        assert 'proved that the proposition' in output and 'false' in output, output
        assert 'unknown module' not in output.lower() and 'object file' not in output.lower(), output
        controls.append({'source': filename, 'source_sha256': digest(ROOT / filename),
                         'exit_code': result.returncode, 'expected_rejection': True})
        control_logs.append(filename + '\n' + output)
    receipt = {
        'schema': 'efa-formal-positional-bridge-receipt-v1',
        'verified_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'explicit finite positional block hypotheses to reduced cubic divisibility, positive quotient construction, coefficient-two cubic strip, and gcd gap',
        'not_formalized': ['Kummer formula', 'extraction of prime-power blocks from P699 failure',
                           'automatic construction of stripped factorization and coprimality data'],
        'external_openai_proofs_rebuilt': False,
        'toolchain_version': version, 'lean_executable': lean,
        'lean_executable_sha256': digest(lean),
        'build_path_base': 'cwd is relative to the bundle root; command file arguments are relative to cwd',
        'builds': builds, 'verifier_sha256': digest(__file__),
        'axiom_audit': audits, 'negative_controls': controls,
    }
    if args.record:
        (ROOT / 'execution.json').write_text(json.dumps(receipt, indent=2) + '\n')
        (ROOT / 'axiom-audit.log').write_text('\n'.join(logs))
        (ROOT / 'negative-controls.log').write_text('\n'.join(control_logs))
    print(json.dumps({'result': 'PASS', 'audited_theorems': len(audits),
                      'negative_controls_rejected': len(controls), 'source_sha256': digest(source)}))

if __name__ == '__main__':
    main()
