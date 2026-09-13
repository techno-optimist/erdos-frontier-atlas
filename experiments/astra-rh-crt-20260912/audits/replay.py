#!/usr/bin/env python3
"""Replay preserved finite checkers only in new external scratch.

This runner verifies byte pins, captures actual output and records dependencies.
It does not verify analytic proofs, download sources or bypass source gates.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
LARGE_RECORDS = {'phase-transfer/check_records.json', 'phase-transfer/actual_interval_records.json'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')


def path_only_output(data, case_root):
    """Substitute only literal/JSON-escaped scratch-root tokens, not math values."""
    root = str(case_root.resolve())
    tokens = {root.encode(): 'literal-utf8'}
    tokens.setdefault(json.dumps(root)[1:-1].encode(), 'json-escaped-ascii')
    tokens.setdefault(json.dumps(root, ensure_ascii=False)[1:-1].encode(), 'json-escaped-utf8')
    public, edits = data, []
    # Longest first avoids matching a literal prefix of an escaped token.
    for original in sorted(tokens, key=len, reverse=True):
        count = public.count(original)
        if count:
            public = public.replace(original, b'.')
            edits.append({
                'kind': 'runtime-path-only', 'token_encoding': tokens[original],
                'original_token_sha256': digest(original),
                'replacement': '.', 'count': count,
            })
    return public, edits


def differences(a, b, path='$'):
    """Report JSON changes instead of silently calling differing receipts equal."""
    if type(a) is not type(b):
        return [path]
    if isinstance(a, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                result.append(path+'.'+key)
            else:
                result.extend(differences(a[key], b[key], path+'.'+key))
        return result
    if isinstance(a, list):
        if len(a) != len(b):
            return [path+'.length']
        return [p for i, (x, y) in enumerate(zip(a, b)) for p in differences(x, y, f'{path}[{i}]')]
    return [] if a == b else [path]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, help='new directory outside this bundle and checkout; must not exist')
    parser.add_argument('--only', help='optional exact checker path from MANIFEST.json')
    args = parser.parse_args()
    out = Path(args.output).resolve()
    checkout = next((p for p in ROOT.parents if (p/'.git').exists()), ROOT)
    if out == ROOT or ROOT in out.parents or out == checkout or checkout in out.parents:
        parser.error('output must be outside this bundle and checkout')
    if out.exists():
        parser.error('output must be a new nonexistent directory')
    manifest = json.loads((ROOT/'MANIFEST.json').read_text())
    specs = manifest['checker_specs']
    if args.only:
        specs = [s for s in specs if s['path'] == args.only]
        if not specs:
            parser.error('unknown checker path')
    expected = {r['public_path']: r['public_sha256']
                for r in manifest['inventory']+manifest['reference_snapshots'] if r.get('public_path')}
    out.mkdir(parents=True)
    record = {
        'schema': 'rh-audit-scratch-replay-v1',
        'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'python_version': sys.version.split()[0],
        'python_executable_label': 'python3 (the interpreter executing this runner)',
        'runner_sha256': digest(Path(__file__).read_bytes()),
        'command': ['python3', '-B', 'replay.py', '--output', '<new-external-scratch>'] + (['--only', args.only] if args.only else []),
        'scope': 'Finite checker process replays, not formal verification, analytic proof validation, literature freshness or an RH claim. Duplicate preserved checker copies count as separate executions, not independent methods.',
        'isolation': 'Each checker receives only its public source and explicitly listed real pinned dependencies in a new per-case directory. Historical result files are never seeded. Raw stdout/stderr and all generated files remain in external scratch; public logs replace only its root with a relative dot.',
        # -B prevents bytecode writes, not assertion removal: override inherited -O settings.
        'environment': {'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1', 'PYTHONHASHSEED': '0', 'PYTHONOPTIMIZE': '0'},
        'runs': [],
        'not_replayed': [s for s in specs if s['status'] != 'standalone-replay'],
    }
    for i, spec in enumerate((s for s in specs if s['status'] == 'standalone-replay'), 1):
        case_id = f'{i:02d}-'+spec['path'].replace('/', '--').replace('.py', '')
        case_root = out/'scratch'/case_id
        case_root.mkdir(parents=True)
        run = {'checker': spec['path'], 'cwd': case_id,
               'command': ['python3', '-B', spec['path']],
               'timeout_seconds': spec['timeout_seconds'],
               'numeric_scope': spec['numeric_scope'],
               'original_checker_sha256': spec['original_sha256'],
               'public_checker_sha256': spec['public_sha256'],
               'copied_inputs': [], 'generated_outputs': []}
        if spec.get('duplicate_of'):
            run['duplicate_of'] = spec['duplicate_of']
        paths = [spec['path']]+spec['dependencies']
        try:
            for rel in paths:
                p = Path(rel)
                if p.is_absolute() or '..' in p.parts:
                    raise ValueError('unsafe input locator')
                b = (ROOT/rel).read_bytes()
                if digest(b) != expected[rel]:
                    raise ValueError('public input hash mismatch: '+rel)
                target = case_root/rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b)
                run['copied_inputs'].append({'path': rel, 'sha256': digest(b)})
        except (OSError, KeyError, ValueError) as e:
            run.update(status='input-integrity-failure', exit_code=None, error=str(e))
            record['runs'].append(run)
            write_json(out/'REPLAY.json', record)
            continue
        env = dict(os.environ, **record['environment'])
        start = time.monotonic()
        try:
            proc = subprocess.run([sys.executable, '-B', spec['path']], cwd=case_root,
                                  env=env, capture_output=True, timeout=spec['timeout_seconds'])
            stdout, stderr = proc.stdout, proc.stderr
            run.update(exit_code=proc.returncode, timed_out=False)
        except subprocess.TimeoutExpired as e:
            stdout, stderr = e.stdout or b'', e.stderr or b''
            run.update(exit_code=None, timed_out=True)
        run['elapsed_seconds'] = round(time.monotonic()-start, 6)
        for stream, data in [('stdout', stdout), ('stderr', stderr)]:
            raw_path = out/'raw-logs'/case_id/(stream+'.txt')
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_bytes(data)
            public, edits = path_only_output(data, case_root)
            public_rel = 'replay/'+case_id+'/'+stream+'.txt'
            public_path = out/public_rel
            public_path.parent.mkdir(parents=True, exist_ok=True)
            public_path.write_bytes(public)
            run[stream] = {'raw_path': raw_path.relative_to(out).as_posix(), 'raw_sha256': digest(data),
                           'raw_size_bytes': len(data), 'public_path': public_rel,
                           'public_sha256': digest(public), 'public_size_bytes': len(public), 'path_edits': edits}
        run['inputs_unchanged'] = all(digest((case_root/r['path']).read_bytes()) == r['sha256'] for r in run['copied_inputs'])
        missing = []
        for rel in spec['outputs']:
            path = case_root/rel
            if not path.is_file():
                missing.append(rel)
                continue
            raw = path.read_bytes()
            public, edits = path_only_output(raw, case_root)
            meta = {'scratch_path': 'scratch/'+case_id+'/'+rel, 'output_locator': rel,
                    'raw_sha256': digest(raw), 'raw_size_bytes': len(raw),
                    'public_sha256': digest(public), 'public_size_bytes': len(public), 'path_edits': edits}
            parsed = json.loads(public)
            if isinstance(parsed, list):
                meta['record_count'] = len(parsed)
                if parsed and isinstance(parsed[0], dict) and 'kind' in parsed[0]:
                    meta['counts_by_kind'] = dict(sorted(Counter(r['kind'] for r in parsed).items()))
            historic = ROOT/rel
            if historic.is_file():
                old = historic.read_bytes()
                meta['historical_public_output_sha256'] = digest(old)
                meta['historical_json_difference_paths'] = differences(json.loads(old), parsed)
            else:
                row = next((r for r in manifest['inventory'] if r['source_locator'] == rel), None)
                if row:
                    meta['historical_original_sha256'] = row['source_sha256']
                    meta['matches_historical_original_bytes'] = digest(raw) == row['source_sha256']
            if rel in LARGE_RECORDS:
                meta.update(public_path=None, disposition='not-copied-to-compact-package; fresh complete records retained in external scratch')
            else:
                public_rel = 'replay/'+case_id+'/outputs/'+rel
                destination = out/public_rel
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(public)
                meta.update(public_path=public_rel, disposition='saved')
            run['generated_outputs'].append(meta)
        run['missing_outputs'] = missing
        run['status'] = ('timeout' if run['timed_out'] else 'passed' if run['exit_code'] == 0 and not missing and run['inputs_unchanged'] else 'failed')
        record['runs'].append(run)
        write_json(out/'REPLAY.json', record)
        print(json.dumps({'checker': spec['path'], 'status': run['status'], 'exit_code': run['exit_code'], 'elapsed_seconds': run['elapsed_seconds']}), flush=True)
    runs = record['runs']
    record['totals'] = {'selected_checker_files': len(specs), 'attempted': sum(r['status'] != 'input-integrity-failure' for r in runs),
                        'passed': sum(r['status']=='passed' for r in runs), 'failed': sum(r['status']=='failed' for r in runs),
                        'timeouts': sum(r['status']=='timeout' for r in runs), 'input_integrity_failures': sum(r['status']=='input-integrity-failure' for r in runs),
                        'not_replayed_excluded_dependencies': len(record['not_replayed']),
                        'duplicate_copy_executions': sum('duplicate_of' in r for r in runs if r['status']!='input-integrity-failure'),
                        'distinct_original_checker_hashes_executed': len({r['original_checker_sha256'] for r in runs if r['status']!='input-integrity-failure'})}
    record['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    write_json(out/'REPLAY.json', record)
    print(json.dumps({'totals': record['totals']}, indent=2))
    return 1 if any(r['status'] != 'passed' for r in runs) else 0


if __name__ == '__main__':
    raise SystemExit(main())
