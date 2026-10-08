#!/usr/bin/env python3
"""Read-only bundle integrity checks; optional exact finite replay, no downloads."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

BUNDLE = Path(__file__).resolve().parent
REPO = BUNDLE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def resolve(relative):
    path = (BUNDLE / relative).resolve()
    require(path.is_relative_to(BUNDLE), f'Indexed path leaves bundle: {relative}')
    require(path.is_file(), f'Missing indexed file: {relative}')
    return path


def pointer(document, keys):
    for key in keys:
        document = document[key]
    return document


def check_hash(expected, path):
    require(re.fullmatch('[0-9a-f]{64}', expected) is not None, f'Invalid digest for {path}')
    require(expected == digest(path), f'Hash mismatch: {path.relative_to(BUNDLE)}')


def local_links():
    checked = 0
    # File existence only: remote targets and heading fragments are not verified.
    for path in sorted(BUNDLE.rglob('*.md')):
        if '.build' in path.parts:
            continue
        text = re.sub(r'```.*?```', '', path.read_text(), flags=re.S)
        targets = re.findall(r'(?<!!)\[[^\]\n]+\]\(([^\s)]+)(?:\s+"[^"]*")?\)', text)
        targets += re.findall(r'^\[[^\]\n]+\]:\s*(\S+)', text, flags=re.M)
        for raw in targets:
            url = raw.strip('<>')
            if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', url) or url.startswith('#'):
                continue
            relative = unquote(url.split('#', 1)[0])
            if not relative:
                continue
            require((path.parent / relative).exists(), f'Broken file link: {path}: {url}')
            checked += 1
    return checked


def check_publication_scope():
    allowed = {'research-sprint', 'research-next', 'swarm', 'upstream-update', 'lead-phase'}
    actual = {p.name for p in BUNDLE.iterdir() if p.is_dir() and p.name != '__pycache__'}
    require(actual == allowed, f'Unexpected mathematical package areas: {sorted(actual ^ allowed)}')
    require({p.name for p in (BUNDLE / 'lead-phase').iterdir()} == {'weighted-formal'},
            'The lead-phase area contains only the weighted proof component')
    return sorted(actual)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay-finite', action='store_true')
    args = parser.parse_args()
    publication_areas = check_publication_scope()
    index = load(BUNDLE / 'evidence-index.json')
    require(index['schema'] == 'efa-evidence-index-v1', 'Unknown index schema')
    levels = {'externally_claimed', 'conditional_deduction', 'local_informal',
              'formal_component', 'finite_evidence', 'source_trace', 'blocked', 'research_proposal'}
    ids = set()
    paths = set()
    for item in index['findings']:
        require(item['id'] not in ids, f'Duplicate finding id: {item["id"]}')
        ids.add(item['id'])
        require(item['evidence_level'] in levels, f'Unknown evidence level: {item["id"]}')
        for relative in item['paths']:
            resolve(relative)
            paths.add(relative)
    hashes = 0
    for check in index['hash_checks']:
        expected = pointer(load(resolve(check['receipt'])), check['field'])
        check_hash(expected, resolve(check['artifact']))
        hashes += 1
    for relative in index['result_manifests']:
        manifest = resolve(relative)
        for result in load(manifest)['results']:
            for receipt in result['receipts']:
                check_hash(receipt['sha256'], manifest.parent / receipt['path'])
                hashes += 1
    # Old model-review hashes are snapshots, not assertions that a mutable note is unchanged.
    snapshots = []
    sprint = BUNDLE / 'research-sprint'
    audit = load(sprint / 'source-audit/audit.json')
    for review in audit['cross_reviews']:
        target = (sprint / 'source-audit' / review['target']).resolve()
        require(target.is_file(), f'Missing reviewed target: {target}')
        if digest(target) != review['reviewed_target_sha256']:
            snapshots.append(str(target.relative_to(BUNDLE)))
    json_count = 0
    for path in BUNDLE.rglob('*.json'):
        if '.build' not in path.parts:
            load(path)
            json_count += 1
    tracked = subprocess.run(['git', 'ls-files', '--', str(BUNDLE.relative_to(REPO))],
                             cwd=REPO, capture_output=True, text=True, check=True).stdout.splitlines()
    junk = [p for p in tracked if '/.build/' in p or '/__pycache__/' in p
            or p.endswith(('.olean', '.ilean', '.pyc', '.o'))]
    require(not junk, f'Tracked build artifacts: {junk}')
    # Negative control: a corrupted receipt digest must be rejected.
    control_path = resolve('research-sprint/arithmetic/verify.py')
    try:
        check_hash('0' * 64, control_path)
    except ValueError:
        pass
    else:
        raise ValueError('Corrupt-hash negative control was accepted')
    replays = []
    if args.replay_finite:
        for replay in index['finite_replays']:
            script = resolve(replay['script'])
            command = [sys.executable, '-I', str(script), *replay.get('args', [])]
            result = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
            require(result.returncode == 0,
                    f'Replay failed: {replay["id"]}\n{result.stdout}\n{result.stderr}')
            if 'compare_json' in replay:
                require(json.loads(result.stdout) == load(resolve(replay['compare_json'])),
                        f'Recomputed finite receipt differs: {replay["id"]}')
            replays.append(replay['id'])
    print(json.dumps({'status': 'passed', 'indexed_findings': len(ids),
                      'indexed_paths': len(paths), 'current_hash_checks': hashes,
                      'json_files_parsed': json_count, 'local_file_links': local_links(),
                      'tracked_build_artifacts': junk,
                      'corrupt_hash_negative_control': 'rejected',
                      'superseded_review_snapshots': snapshots,
                      'finite_replays': replays,
                      'mathematical_publication_areas': publication_areas,
                      'lean_rebuilt': False, 'external_proofs_verified': False}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        raise SystemExit(1)
