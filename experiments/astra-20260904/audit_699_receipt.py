#!/usr/bin/env python3
"""P699 semantic audit: original and proposed guard on temporary copies.

The exit code is 0 when the REPRODUCTION succeeds, including observing the
original checker defect. No frozen certificate is edited. Not a math refutation.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
args = parser.parse_args()
source = args.repo / 'certificates' / 'erdos-699'

with tempfile.TemporaryDirectory(prefix='erdos-699-audit-') as temp:
    target = Path(temp)
    for name in ('exact.py', 'reference.py', 'verify.py', 'RESULT.json'):
        shutil.copyfile(source / name, target / name)
    original = json.loads((target / 'RESULT.json').read_text())
    assert original['counterexamples'] == 0
    assert all(s['counterexamples'] == 0 for s in original['shards'])
    original['counterexamples'] = 1
    original['shards'][0]['counterexamples'] = 1
    (target / 'RESULT.json').write_text(json.dumps(original))

    before = subprocess.run([sys.executable, '-I', str(target / 'verify.py'), '--quick'],
                            capture_output=True, text=True)
    assert before.returncode == 0, before.stdout + before.stderr
    before_verdict = json.loads(before.stdout.strip().splitlines()[-1])
    assert before_verdict['verified'] and before_verdict['counterexamples'] == 0

    # A minimal proposed repair, tested only in this disposable copy.
    text = (target / 'verify.py').read_text()
    anchor = '          "counterexample counts add up")'
    assert text.count(anchor) == 1
    replacement = anchor + '''
    check(type(result["counterexamples"]) is int and result["counterexamples"] == 0
          and all(type(s["counterexamples"]) is int and s["counterexamples"] == 0
                  for s in sh), "zero counterexamples in every shard and in total")'''
    (target / 'verify.py').write_text(text.replace(anchor, replacement))
    after = subprocess.run([sys.executable, '-I', str(target / 'verify.py'), '--quick'],
                           capture_output=True, text=True)
    assert after.returncode != 0, after.stdout + after.stderr
    after_verdict = json.loads(after.stdout.strip().splitlines()[-1])
    assert after_verdict['verified'] is False

    # The guard must still accept the untouched published zero-count receipt.
    shutil.copyfile(source / 'RESULT.json', target / 'RESULT.json')
    clean = subprocess.run([sys.executable, '-I', str(target / 'verify.py'), '--quick'],
                           capture_output=True, text=True)
    assert clean.returncode == 0, clean.stdout + clean.stderr
    clean_verdict = json.loads(clean.stdout.strip().splitlines()[-1])
    assert clean_verdict['verified'] and clean_verdict['counterexamples'] == 0

    print(json.dumps({
        'scope': 'standalone semantic checker only; repository hash gates not tested',
        'frozen_files_modified': False,
        'mutated_receipt_counterexamples': 1,
        'original_checker': {'exit_code': before.returncode, 'verdict': before_verdict},
        'proposed_guard_mutated_receipt': {'exit_code': after.returncode, 'verdict': after_verdict},
        'proposed_guard_clean_receipt': {'exit_code': clean.returncode, 'verdict': clean_verdict}
    }, indent=2))
