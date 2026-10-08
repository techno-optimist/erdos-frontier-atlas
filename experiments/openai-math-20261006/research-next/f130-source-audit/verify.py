"""Offline F130 byte/import/text audit. Never invokes Lean, Lake, or the network."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
COMMIT = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
BASE = 'https://raw.githubusercontent.com/OpenAI/math/' + COMMIT + '/'
SNAPSHOT = '7f667ac5a922bc867eefacf7115ef09393b1dd143c902e1543ff530b8ee0dee8'
SOURCE_MAP = '190c84342ea257ffe254f2947d25af274e8a3f75ac85c707d2a616169f7dd68f'
LICENSE = 'c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4'
GOALS = ['paperM','paperW','paperDelta','paperMultiplier','theta','decimalExponent',
         'paperTime','decimalTime','nlogn','dft','conv','DFTProgram','ConvProgram',
         'TimeBounds','DFTGoal','ConvGoal']


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def decode(raw):
    def pairs(values):
        out = {}
        for key, value in values:
            need(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    def reject(value):
        raise ValueError('nonfinite JSON constant')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject)


def relative(name):
    need(type(name) is str and name and '\\' not in name, 'relative filename')
    need(not Path(name).is_absolute() and all(p not in ('', '.', '..') for p in name.split('/')), 'canonical relative filename')
    return name


def read(name):
    path = HERE / relative(name)
    need(all(not p.is_symlink() for p in (path, *path.parents)), 'linked artifact refused')
    need(path.is_file() and path.stat().st_size <= 2*1024*1024, 'bounded regular artifact')
    with path.open('rb') as stream:
        raw = stream.read(2*1024*1024+1)
    need(len(raw) <= 2*1024*1024, 'bounded read')
    return raw


def check_bytes(raw, row):
    need(type(row['bytes']) is int and row['bytes'] >= 0 and len(raw) == row['bytes'], 'artifact length')
    need(type(row['sha256']) is str and sha(raw) == row['sha256'], 'artifact hash')


def clean(text):
    """Lexical helper only: remove nested comments and quoted strings, not Lean parsing."""
    out = []; i = 0; depth = 0; string = False
    while i < len(text):
        if depth:
            if text.startswith('/-', i): depth += 1; i += 2
            elif text.startswith('-/', i): depth -= 1; i += 2
            else: i += 1
        elif string:
            if text[i] == '\\': i += 2
            elif text[i] == '"': string = False; i += 1
            else: i += 1
        elif text.startswith('/-', i): depth = 1; i += 2
        elif text.startswith('--', i):
            end = text.find('\n', i); i = len(text) if end < 0 else end
        elif text[i] == '"': string = True; i += 1
        else: out.append(text[i]); i += 1
    need(depth == 0 and not string, 'unterminated lexical comment/string')
    return ''.join(out)


def norm(text):
    return re.sub(r'\s+', '', clean(text))


def definition(text, name):
    text = clean(text)
    found = re.search(r'^def ' + re.escape(name) + r'\b', text, re.M)
    need(found is not None, 'definition missing: ' + name)
    rest = text[found.start():]
    end = re.search(r'\n(?:def|abbrev|theorem|end)\b', rest)
    return rest[:end.start()] if end else rest


def ram_block(text):
    start = 'namespace PowerSaving\n\nuniverse'
    end = 'end RAM\nend PowerSaving'
    need(start in text and end in text, 'RAM block markers')
    return text[text.index(start):text.index(end)+len(end)]


def import_lines(text):
    imports = []
    for line in text.splitlines():
        if re.match(r'^\s*import\b', line):
            fields = line.split()
            need(line.startswith('import ') and len(fields) == 2, 'unsupported import syntax; inspect before extending scan')
            imports.append(fields[1])
    return imports


def closure(sources):
    todo = ['OAI.Computability.FourierTransform.Main']; seen = set(); external = set()
    while todo:
        module = todo.pop()
        if module in seen: continue
        path = 'lean/' + module.replace('.', '/') + '.lean'
        need(path in sources, 'local import absent: ' + module)
        seen.add(module)
        for item in import_lines(sources[path].decode()):
            if item.startswith('OAI.'): todo.append(item)
            else: external.add(item)
    return seen, external


def controls():
    refusals = []
    def no(name, call):
        try: call()
        except (ValueError, KeyError): refusals.append(name); return
        raise ValueError('control unexpectedly admitted: ' + name)
    no('changed_byte', lambda: check_bytes(b'x', {'bytes':1,'sha256':sha(b'y')}))
    no('boolean_length', lambda: check_bytes(b'x', {'bytes':True,'sha256':sha(b'x')}))
    no('path_escape', lambda: relative('../source'))
    no('absolute_path', lambda: relative('/source'))
    no('duplicate_json', lambda: decode(b'{"a":1,"a":2}'))
    no('nonfinite_json', lambda: decode(b'{"a":NaN}'))
    no('missing_import', lambda: closure({'lean/OAI/Computability/FourierTransform/Main.lean':b'import OAI.Missing\n'}))
    no('multiple_imports_on_line', lambda: import_lines('import OAI.A OAI.B'))
    no('unterminated_comment', lambda: clean('/- incomplete'))
    no('unterminated_string', lambda: clean('"incomplete'))
    no('missing_definition', lambda: definition('def x := 0', 'y'))
    need(norm('/- sorry /- axiom -/ -/ def x := "unsafe" -- admit\n 1') == 'defx:=1', 'lexical comment/string control')
    need(norm(definition('def DFTGoal := True\nend', 'DFTGoal')) !=
         norm(definition('def DFTGoal := False\nend', 'DFTGoal')), 'changed proposition distinguished')
    need(encode({'checked':True}) != encode({'checked':1}), 'typed receipt distinction')
    return dict(refusals=refusals, positive_controls=3)


def verify():
    storage = decode(read('snapshot-storage.json'))
    need(storage['snapshot_manifest_sha256'] == SNAPSHOT, 'snapshot pin')
    files = {}
    targets = set()
    for row in storage['files']:
        name = relative(row['logical_snapshot_path']); target = relative(row['stored_path'])
        need(name not in files and target not in targets, 'unique snapshot paths')
        expected = 'snapshot/' + name + ('.txt' if name.startswith('source/') and name.endswith('.md') else '')
        need(target == expected, 'declared raw Markdown storage mapping')
        raw = read(target); check_bytes(raw, row); files[name] = raw; targets.add(target)
    need(len(files) == 104 and sha(files['manifest.json']) == SNAPSHOT, 'frozen snapshot inventory')
    original = decode(files['manifest.json'])
    need({r['path'] for r in original['files']} == set(files)-{'manifest.json'}, 'original full snapshot closure')
    for row in original['files']: check_bytes(files[row['path']], row)
    need(sha(files['source-manifest.json']) == SOURCE_MAP, 'source map pin')
    source_map = decode(files['source-manifest.json'])
    need(source_map['commit'] == COMMIT and len(source_map['files']) == 97, 'source commit/count')
    sources = {}
    for name, row in source_map['files'].items():
        need(row['url'] == BASE + name, 'exact public source URL')
        raw = files['source/'+name]; check_bytes(raw, row); sources[name] = raw
        if name.endswith('.lean'):
            need(import_lines(raw.decode()) == row['imports'], 'source import metadata')
    need(sum(map(len,sources.values())) == source_map['total_bytes'] == 645234, 'source byte total')
    modules, external = closure(sources)
    need(len(modules) == 89 and external == {'Mathlib'}, 'bounded local proof closure')
    need({'lean/'+m.replace('.','/')+'.lean' for m in modules} ==
         {p for p in sources if p.startswith('lean/OAI/')}, 'no extra/missing local proof source')
    C=sources['lean/ComparatorChallenges/UniformFourier.lean'].decode()
    R=sources['lean/OAI/Computability/FourierTransform/RAM.lean'].decode()
    G=sources['lean/OAI/Computability/FourierTransform/Goal.lean'].decode()
    matches={n:norm(definition(C,n))==norm(definition(G,n)) for n in GOALS}
    flags={}
    for path,raw in sources.items():
        if path.startswith('lean/OAI/'):
            tokens=re.findall(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',clean(raw.decode()))
            if tokens: flags[path]=tokens
    reconstructed=dict(schema='uniform-fourier-static-source-checks/v1',commit=COMMIT,
        local_proof_module_count=89,source_snapshot_sha256=SOURCE_MAP,
        ram_comment_whitespace_normalized_match=norm(ram_block(C))==norm(ram_block(R)),
        goal_definition_comment_whitespace_normalized_matches=matches,local_proof_source_token_flags=flags,
        scan_kind='Lexical only; removes nested comments and double-quoted strings. Not a parser or transitive Lean axiom audit.',
        lean_compilation_performed=False,declaration_export_performed=False,kernel_check_performed=False,
        comparator_performed=False,dependency_packages_fetched=False)
    need(encode(reconstructed)==encode(decode(files['static-source-checks.json'])), 'complete saved static-receipt replay')
    need(all(matches.values()) and reconstructed['ram_comment_whitespace_normalized_match'] and not flags, 'static outcomes')
    specification=decode(sources['lean/ComparatorChallenges/UniformFourier.json'])
    need(specification == dict(challenge_module='ComparatorChallenges.UniformFourier',
        solution_module='OAI.Computability.FourierTransform.Main',
        theorem_names=['OAI.PowerSaving.transform_main','OAI.PowerSaving.convolution_main'],
        definition_names=[],permitted_axioms=['propext','Quot.sound','Classical.choice'],enable_nanoda=False), 'exact comparator configuration')
    provenance=decode(read('provenance.json'))
    need(provenance['commit']==COMMIT and provenance['license_identifier']=='Apache-2.0'
         and provenance['upstream_root_notice_present'] is False, 'license metadata')
    for row in provenance['assets']:check_bytes(read(row['path']),row)
    need(sha(read('UPSTREAM_LICENSE'))==LICENSE, 'exact upstream license')
    listing=decode(read('upstream-root-listing.json'))
    need(any(x['name']=='LICENSE' and x['type']=='file' for x in listing)
         and not any(x['name']=='NOTICE' for x in listing), 'recorded upstream root listing')
    need(b'Apache License' in read('UPSTREAM_LICENSE') and b'Version 2.0' in read('UPSTREAM_LICENSE'), 'license inspection markers')
    return dict(schema='f130-offline-packet-receipt/v1',status='passed',commit=COMMIT,
        snapshot_manifest_sha256=SNAPSHOT,source_manifest_sha256=SOURCE_MAP,
        original_snapshot_files=104,upstream_source_files=97,upstream_source_bytes=645234,
        local_proof_modules=89,external_proof_imports=sorted(external),
        normalized_ram_match=True,normalized_goal_definitions=matches,
        original_static_receipt_exactly_replayed=True,upstream_source_bytes_modified=False,
        license_sha256=LICENSE,controls=controls(),verifier_sha256=sha(read('verify.py')),
        boundary=dict(offline=True,network_calls=0,lean_build=False,lake_execution=False,
                      dependency_download=False,comparator_run=False,axiom_export=False,
                      performance_measurement=False,novelty_claim=False))


def check_manifest():
    manifest=decode(read('manifest.json'))
    names=set()
    for row in manifest['files']:
        need(row['path'] not in names, 'unique final inventory'); names.add(row['path'])
        check_bytes(read(row['path']), row)
    actual={p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
    need(actual==names|{'manifest.json'}, 'exact complete packet inventory')


def main():
    parser=argparse.ArgumentParser();choice=parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--write',action='store_true');choice.add_argument('--check',action='store_true')
    args=parser.parse_args();result=verify();raw=encode(result)
    if args.write:
        with (HERE/'receipt.json').open('xb') as stream:stream.write(raw)
    else:
        need(read('receipt.json')==raw,'exact packet receipt replay');check_manifest()
    print(json.dumps(dict(status='passed',source_files=97,local_modules=89,
                          static_definitions=16,refusals=len(result['controls']['refusals']),lean_build=False),sort_keys=True))


if __name__=='__main__':main()
