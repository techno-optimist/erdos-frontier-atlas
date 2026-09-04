"""Displayed tables must be consumed completely, not as numeric prefixes."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).parent
BLOCK = HERE / 'block'
# One entry in each table; the first two share their line with another entry.
ENTRIES = ('(1,0): 6,14,28', '(1,5,1): 48,112,112', '(1,1,1): 15')
ENDS = ('This closes the induction.', '**Isolated-P lemma.**',
        'Thus the unit-scalar result')


class BlockTablesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = (BLOCK / 'RESULT.md').read_text()
        cls.fixture = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.fixture.cleanup)
        cls.root = Path(cls.fixture.name)
        for name in ('review_check.py', 'check.py', 'receipt.json'):
            shutil.copyfile(BLOCK / name, cls.root / name)

    def run_review(self, text):
        # Never corrupt the proof or receipts in the working tree.
        (self.root / 'RESULT.md').write_text(text)
        return subprocess.run(
            [sys.executable, '-I', '-B', str(self.root / 'review_check.py'),
             '--replay-bound', '1'],
            capture_output=True, text=True, timeout=30,
        )

    def assert_rejected(self, text):
        result = self.run_review(text)
        self.assertNotEqual(result.returncode, 0,
                            'Malformed displayed table was accepted')
        self.assertEqual(result.stdout, '')
        self.assertRegex(result.stderr, r'(AssertionError|ValueError)')

    def assert_accepted(self, text):
        result = self.run_review(text)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'PASS')
        self.assertTrue(data['printed_tables_match'])
        self.assertEqual(data['independent_base_counts'], [16, 15, 20])
        self.assertEqual(data['replayed_blocks'], 1)

    def test_current_valid_tables_pass(self):
        self.assert_accepted(self.original)

    def test_whitespace_and_multiple_entries_per_line_pass(self):
        text = self.original.replace(
            '(1,0): 6,14,28      (1,2)', '(1,0):\t6,14,28 \t (1,2)')
        text = text.replace('    (1,1,2):', '\n\t    (1,1,2):')
        text = text.replace('(1,1,1): 15\n', '(1,1,1): 15 \t\n')
        self.assert_accepted(text)

    def test_decimal_values_are_rejected(self):
        for entry in ENTRIES:
            with self.subTest(entry=entry):
                self.assert_rejected(self.original.replace(entry, entry + '.5', 1))

    def test_trailing_negative_values_are_rejected(self):
        for entry in ENTRIES:
            with self.subTest(entry=entry):
                self.assert_rejected(self.original.replace(entry, entry + ',-999', 1))

    def test_other_unconsumed_suffixes_are_rejected(self):
        for suffix in (',', 'e2', '+0', ' junk'):
            with self.subTest(suffix=suffix):
                entry = ENTRIES[2]
                self.assert_rejected(self.original.replace(entry, entry + suffix, 1))

    def test_leading_junk_is_rejected(self):
        for entry in ENTRIES:
            with self.subTest(entry=entry):
                self.assert_rejected(self.original.replace(
                    '    ' + entry, '    junk ' + entry, 1))

    def test_junk_line_before_first_small_entry_is_rejected(self):
        self.assert_rejected(self.original.replace(
            '    ' + ENTRIES[2], '    junk\n    ' + ENTRIES[2], 1))

    def test_junk_lines_at_table_ends_are_rejected(self):
        for end in ENDS:
            with self.subTest(end=end):
                self.assert_rejected(self.original.replace(end, '    junk\n\n' + end, 1))

    def test_malformed_extra_duplicate_entries_are_rejected(self):
        for entry, end in zip(ENTRIES, ENDS):
            duplicate = entry.split(':')[0] + ': -999'
            for position in ('same_line', 'new_line'):
                with self.subTest(entry=entry, position=position):
                    if position == 'same_line':
                        text = self.original.replace(entry, entry + '   ' + duplicate, 1)
                    else:
                        text = self.original.replace(end, '    ' + duplicate + '\n\n' + end, 1)
                    self.assert_rejected(text)

    def test_valid_extra_duplicate_entries_are_rejected(self):
        for entry, end in zip(ENTRIES, ENDS):
            with self.subTest(entry=entry):
                self.assert_rejected(self.original.replace(end, '    ' + entry + '\n\n' + end, 1))

    def test_junk_after_literal_headers_is_rejected(self):
        for header in ('(a,b): differences', '(r,s,t): differences'):
            with self.subTest(header=header):
                self.assert_rejected(self.original.replace(header, header + ' junk', 1))


if __name__ == '__main__':
    unittest.main()
