#!/usr/bin/env python3
"""Compile the local proof and require both deliberately false controls to fail."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
EXPECTED_VERSION = 'Lean (version 4.33.1,'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
AUDIT_NAMES = [
    'discrepancy_balance', 'one_sided_transport', 'count_stability',
    'intersection_stability', 'intersection_one_sided_transport',
    'joint_event_stability', 'joint_one_sided_transport', 'joint_count_transport',
    'sublinear_add', 'asymptotic_joint_transport', 'asymptotic_joint_from_marginals',
    'count_gap_le_discrepancy', 'asymptotic_joint_count_gap',
]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, **kwargs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', default=shutil.which('lean'))
    parser.add_argument('--record', action='store_true', help='write this execution receipt')
    args = parser.parse_args()
    if not args.lean:
        parser.error('pass --lean /absolute/path/to/the/official/4.33.1/bin/lean')
    lean = str(Path(args.lean).resolve())
    version_result = run([lean, '--version'])
    version = version_result.stdout.strip()
    assert version_result.returncode == 0 and version.startswith(EXPECTED_VERSION), version
    source = ROOT / 'DensityTransport.lean'
    assert not re.search(r'\b(sorry|admit|axiom)\b', source.read_text()), 'untrusted proof declaration'
    build = ROOT / '.build'
    build.mkdir(exist_ok=True)
    result = run([lean, '-o', str(build / 'DensityTransport.olean'), source.name])
    output = result.stdout + result.stderr
    if result.returncode:
        print(output)
        raise SystemExit(result.returncode)
    assert 'sorryAx' not in output, 'untrusted axiom dependency'
    audits = {}
    for name in AUDIT_NAMES:
        pattern = r"'DensityTransport\." + re.escape(name) + r"' depends on axioms: \[([^\]]*)\]"
        match = re.search(pattern, output)
        if match:
            axioms = [x.strip() for x in match.group(1).split(',') if x.strip()]
        else:
            assert f"'DensityTransport.{name}' does not depend on any axioms" in output, (name, output)
            axioms = []
        assert set(axioms) <= ALLOWED_AXIOMS, (name, axioms)
        audits[name] = axioms
    env = dict(os.environ)
    env['LEAN_PATH'] = str(build)
    controls = []
    control_logs = []
    for filename in ['negative/OmitMarginal.lean', 'negative/OmitLeakage.lean']:
        negative = run([lean, filename], env=env)
        log = negative.stdout + negative.stderr
        assert negative.returncode != 0, f'false statement unexpectedly accepted: {filename}'
        assert 'error:' in log and ('false' in log.lower() or 'decide' in log.lower()), log
        assert 'unknown module' not in log.lower() and 'object file' not in log.lower(), log
        controls.append({'path': filename, 'expected_rejection': True, 'exit_code': negative.returncode,
                         'source_sha256': digest(ROOT / filename)})
        control_logs.append(filename + '\n' + log)
    receipt = {
        'schema': 'efa-density-transport-lean-receipt-v1',
        'verified_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'verification_scope': 'local explicit-hypothesis finite and natural-number-sublinear transport proofs only',
        'external_openai_proofs_rebuilt': False,
        'toolchain_version': version,
        'lean_executable': lean,
        'lean_executable_sha256': digest(lean),
        'official_release_url': 'https://github.com/leanprover/lean4/releases/tag/v4.33.1',
        'official_darwin_arm64_archive_sha256': '88c45aad985b5d2a8d925fe10bd1296bd35f66f408480ab182d3facccd065a9d',
        'compile_command': [lean, '-o', '.build/DensityTransport.olean', 'DensityTransport.lean'],
        'compile_exit_code': result.returncode,
        'source_sha256': digest(source),
        'verifier_sha256': digest(Path(__file__)),
        'axiom_audit': audits,
        'negative_controls': controls,
        'proof_olean_sha256': digest(build / 'DensityTransport.olean'),
    }
    if args.record:
        (ROOT / 'execution.json').write_text(json.dumps(receipt, indent=2) + '\n')
        (ROOT / 'axiom-audit.log').write_text(output)
        (ROOT / 'negative-controls.log').write_text('\n'.join(control_logs))
    print(json.dumps({'result': 'PASS', 'audited_theorems': len(audits),
                      'negative_controls_rejected': len(controls), 'toolchain': version}))

if __name__ == '__main__':
    main()
