"""The block checker must reject an empty requested sweep."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).parent


class BlockCliTest(unittest.TestCase):
    def run_bound(self, bound):
        return subprocess.run(
            [sys.executable, '-I', '-B', str(HERE / 'block' / 'check.py'),
             '--bound', str(bound)],
            capture_output=True, text=True, timeout=30,
        )

    def assert_invalid_bound(self, bound):
        result = self.run_bound(bound)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertIn('usage:', result.stderr)
        self.assertIn('error: --bound must be at least 1', result.stderr)

    def test_zero_bound_is_rejected(self):
        self.assert_invalid_bound(0)

    def test_negative_bound_is_rejected(self):
        self.assert_invalid_bound(-1)

    def test_bound_one_checks_one_block(self):
        result = self.run_bound(1)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'PASS')
        self.assertEqual(data['checked'], 1)
        self.assertEqual(data['bound'], 1)


if __name__ == '__main__':
    unittest.main()
