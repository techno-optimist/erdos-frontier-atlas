"""Packaging harness smoke test using a real preserved checker (no new math)."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


class ReplayHarnessTest(unittest.TestCase):
    def test_real_checker_runs_in_fresh_scratch_and_saves_output(self):
        with tempfile.TemporaryDirectory(prefix='audit-harness-test-') as outer:
            out = Path(outer)/'fresh-run'
            proc = subprocess.run([sys.executable, '-B', 'replay.py', '--output', str(out),
                                   '--only', 'gm-candidate/check_exponents.py'],
                                  cwd=ROOT, capture_output=True, timeout=45)
            self.assertEqual(proc.returncode, 0, proc.stderr.decode())
            record = json.loads((out/'REPLAY.json').read_text())
            self.assertEqual(record['totals']['attempted'], 1)
            self.assertEqual(record['totals']['passed'], 1)
            run = record['runs'][0]
            self.assertEqual(run['exit_code'], 0)
            self.assertEqual(run['command'], ['python3', '-B', 'gm-candidate/check_exponents.py'])
            self.assertTrue(run['inputs_unchanged'])
            self.assertFalse(Path(run['cwd']).is_absolute())
            stdout = out/run['stdout']['public_path']
            self.assertEqual(hashlib.sha256(stdout.read_bytes()).hexdigest(), run['stdout']['public_sha256'])
            self.assertTrue(json.loads(stdout.read_text())['all_assertions_passed'])
            self.assertFalse(str(Path(outer).resolve()) in (out/'REPLAY.json').read_text())
            self.assertTrue((out/'scratch'/run['cwd']/'gm-candidate/exponent-results.json').is_file())

    def _assert_duplicate_input_failure_is_not_an_execution(self, checker, missing):
        def hashes(root):
            return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in root.rglob('*') if p.is_file()}

        archive_before = hashes(ROOT)
        with tempfile.TemporaryDirectory(prefix='audit-duplicate-input-test-') as outer:
            bundle = Path(outer)/'bundle'
            bundle.mkdir()
            manifest = json.loads((ROOT/'MANIFEST.json').read_text())
            spec = next(s for s in manifest['checker_specs'] if s['path'] == checker)
            self.assertTrue(spec['duplicate_of'])
            # Real sources and their unchanged byte pins, never historical outputs
            # or placeholders for excluded inputs. Damage only the scratch copy.
            for rel in ['replay.py', 'MANIFEST.json', checker]+spec['dependencies']:
                target = bundle/rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/rel, target)
            if missing:
                (bundle/checker).unlink()
            else:
                (bundle/checker).write_bytes((bundle/checker).read_bytes()+b'\n')
            bundle_before = hashes(bundle)
            out = Path(outer)/'fresh-run'
            proc = subprocess.run([sys.executable, '-B', str(bundle/'replay.py'),
                                   '--output', str(out), '--only', checker],
                                  cwd=outer, capture_output=True, timeout=45)
            self.assertEqual(proc.returncode, 1, proc.stdout.decode()+proc.stderr.decode())
            record = json.loads((out/'REPLAY.json').read_text())
            self.assertEqual(len(record['runs']), 1)
            run = record['runs'][0]
            self.assertEqual(run['status'], 'input-integrity-failure')
            self.assertEqual(run['duplicate_of'], spec['duplicate_of'])
            self.assertIsNone(run['exit_code'])
            self.assertIn(checker, run['error'])
            self.assertIn('No such file or directory' if missing else 'public input hash mismatch', run['error'])
            self.assertEqual(run['copied_inputs'], [])
            self.assertEqual(run['generated_outputs'], [])
            self.assertFalse((out/'raw-logs').exists())
            self.assertEqual(hashes(out/'scratch'/run['cwd']), {})
            self.assertFalse({'elapsed_seconds', 'timed_out', 'stdout', 'stderr'} & run.keys())
            # Check preservation even when the final execution-count assertion fails.
            self.assertEqual(hashes(bundle), bundle_before)
            self.assertEqual(hashes(ROOT), archive_before)
            self.assertEqual(record['totals'], {
                'selected_checker_files': 1, 'attempted': 0, 'passed': 0, 'failed': 0,
                'timeouts': 0, 'input_integrity_failures': 1,
                'not_replayed_excluded_dependencies': 0, 'duplicate_copy_executions': 0,
                'distinct_original_checker_hashes_executed': 0,
            })

    def test_missing_duplicate_source_is_not_an_execution(self):
        self._assert_duplicate_input_failure_is_not_an_execution(
            'gm-first/original_check_exponents.py', missing=True)

    def test_hash_mismatched_duplicate_source_is_not_an_execution(self):
        self._assert_duplicate_input_failure_is_not_an_execution(
            'sparse-square/replayed-original/check_algebra.py', missing=False)

    def test_inherited_optimization_cannot_bypass_historical_assertion(self):
        checker = 'gm-second/compare_critical_bounds.py'
        parameter = 'inputs/gm_parameter_check.json'
        with tempfile.TemporaryDirectory(prefix='audit-assertion-test-') as outer:
            bundle = Path(outer)/'bundle'
            bundle.mkdir()
            manifest = json.loads((ROOT/'MANIFEST.json').read_text())
            spec = next(s for s in manifest['checker_specs'] if s['path'] == checker)
            # Only the real checker and its explicit input, never historical outputs
            # or stand-ins for excluded sources. The archive itself stays untouched.
            for rel in ['replay.py', checker]+spec['dependencies']:
                target = bundle/rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/rel, target)
            data = json.loads((bundle/parameter).read_text())
            data['margins'][0]['remaining_coefficients'][0] = '0'
            poisoned = (json.dumps(data, indent=2)+'\n').encode()
            (bundle/parameter).write_bytes(poisoned)
            # Deliberately repin only this scratch fixture to exercise the historical
            # assertion, independently of the runner's input-byte integrity gate.
            ref = next(r for r in manifest['reference_snapshots'] if r.get('public_path') == parameter)
            ref.update(public_sha256=hashlib.sha256(poisoned).hexdigest(), public_size_bytes=len(poisoned))
            (bundle/'MANIFEST.json').write_text(json.dumps(manifest))
            expected_inputs = [{'path': rel, 'sha256': hashlib.sha256((bundle/rel).read_bytes()).hexdigest()}
                               for rel in [checker]+spec['dependencies']]
            for optimize in ['0', '1', '2']:
                with self.subTest(PYTHONOPTIMIZE=optimize):
                    out = Path(outer)/('optimize-'+optimize)
                    proc = subprocess.run([sys.executable, '-B', str(bundle/'replay.py'),
                                           '--output', str(out), '--only', checker],
                                          cwd=outer, env=dict(os.environ, PYTHONOPTIMIZE=optimize),
                                          capture_output=True, timeout=45)
                    record = json.loads((out/'REPLAY.json').read_text())
                    run = record['runs'][0]
                    self.assertEqual(run['copied_inputs'], expected_inputs)
                    self.assertTrue(run['inputs_unchanged'])
                    self.assertEqual(proc.returncode, 1, proc.stdout.decode())
                    self.assertEqual(run['status'], 'failed')
                    self.assertEqual(run['exit_code'], 1)
                    stderr = (out/run['stderr']['raw_path']).read_text()
                    self.assertIn('line 59', stderr)
                    self.assertIn('AssertionError', stderr)
                    self.assertEqual(run['generated_outputs'], [])
                    self.assertEqual(record['environment'].get('PYTHONOPTIMIZE'), '0')
            self.assertEqual((bundle/checker).read_bytes(), (ROOT/checker).read_bytes())

    def test_json_escaped_roots_are_normalized_in_real_checker_public_outputs(self):
        checker = 'gm-second/compare_critical_bounds.py'
        parameter = 'inputs/gm_parameter_check.json'
        with tempfile.TemporaryDirectory(prefix='audit-path-test-') as outer:
            for label in ['unicode-π', 'quote-"', 'backslash-\\', 'combined-π"\\']:
                with self.subTest(path=label):
                    out = Path(outer)/label
                    proc = subprocess.run([sys.executable, '-B', 'replay.py', '--output', str(out),
                                           '--only', checker], cwd=ROOT, capture_output=True, timeout=45)
                    self.assertEqual(proc.returncode, 0, proc.stderr.decode())
                    record = json.loads((out/'REPLAY.json').read_text())
                    run = record['runs'][0]
                    case_root = (out/'scratch'/run['cwd']).resolve()
                    token = json.dumps(str(case_root))[1:-1].encode()
                    self.assertEqual(run['status'], 'passed')
                    artifacts = [(run['stdout'], 'raw_path'),
                                 (run['generated_outputs'][0], 'scratch_path')]
                    for meta, raw_key in artifacts:
                        raw = (out/meta[raw_key]).read_bytes()
                        public = (out/meta['public_path']).read_bytes()
                        self.assertEqual(json.loads(raw)['parent_input'], str(case_root/parameter))
                        self.assertEqual(json.loads(public)['parent_input'], './'+parameter)
                        # Verify exact byte edits, not a parse-and-reserialize rewrite.
                        self.assertEqual(public, raw.replace(token, b'.'))
                        self.assertEqual(meta['path_edits'], [{
                            'kind': 'runtime-path-only', 'token_encoding': 'json-escaped-ascii',
                            'original_token_sha256': hashlib.sha256(token).hexdigest(),
                            'replacement': '.', 'count': raw.count(token),
                        }])
                        self.assertEqual(hashlib.sha256(raw).hexdigest(), meta['raw_sha256'])
                        self.assertEqual(hashlib.sha256(public).hexdigest(), meta['public_sha256'])
                    self.assertEqual((out/'scratch'/run['cwd']/checker).read_bytes(), (ROOT/checker).read_bytes())

    def test_path_only_edits_preserve_other_bytes_across_literal_and_json_forms(self):
        normalize = runpy.run_path(str(ROOT/'replay.py'))['path_only_output']
        with tempfile.TemporaryDirectory(prefix='audit-token-test-') as outer:
            root = Path(outer)/'π"\\'
            literal = str(root.resolve()).encode()
            ascii_token = json.dumps(str(root.resolve()))[1:-1].encode()
            utf8_token = json.dumps(str(root.resolve()), ensure_ascii=False)[1:-1].encode()
            unchanged = b'\n{"math": ["17/28", -3, 1.25], "other_path": "/elsewhere/\\u03c0\\\\\\\""}\n'
            raw = (literal+b'/plain\n"'+ascii_token+b'/ascii"\n"'+utf8_token+b'/utf8"\n'
                   +literal+b'/again'+unchanged)
            public, edits = normalize(raw, root)
            self.assertEqual(public, b'./plain\n"./ascii"\n"./utf8"\n./again'+unchanged)
            forms = {'literal-utf8': literal, 'json-escaped-ascii': ascii_token, 'json-escaped-utf8': utf8_token}
            self.assertEqual({edit['token_encoding'] for edit in edits}, set(forms))
            reconstructed = raw
            for edit in edits:
                token = forms[edit['token_encoding']]
                self.assertEqual(edit['kind'], 'runtime-path-only')
                self.assertEqual(edit['original_token_sha256'], hashlib.sha256(token).hexdigest())
                self.assertEqual(edit['replacement'], '.')
                self.assertEqual(edit['count'], reconstructed.count(token))
                reconstructed = reconstructed.replace(token, b'.')
            self.assertEqual(reconstructed, public)
            self.assertEqual(normalize(unchanged, root), (unchanged, []))
            # An ordinary root has identical literal and JSON tokens: count it once.
            plain_root = Path(outer)/'plain-root'
            plain = str(plain_root.resolve()).encode()
            normalized, plain_edits = normalize(plain+b'\n'+plain, plain_root)
            self.assertEqual(normalized, b'.\n.')
            self.assertEqual(len(plain_edits), 1)
            self.assertEqual(plain_edits[0]['count'], 2)


if __name__ == '__main__':
    unittest.main()
