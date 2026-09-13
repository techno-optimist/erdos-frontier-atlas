"""The CRT checker must verify evidence, not silently overwrite it."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).parent


class BridgeReceiptTest(unittest.TestCase):
    def test_readonly_replay_and_poisoned_count(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            for name in ('check_bridge.py', 'checks.json'):
                shutil.copy2(HERE / 'bridge' / name, target / name)
            receipt = target / 'checks.json'
            before = receipt.stat().st_mtime_ns
            result = subprocess.run([sys.executable, '-I', str(target / 'check_bridge.py')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(receipt.stat().st_mtime_ns, before, 'replay rewrote evidence')
            data = json.loads(receipt.read_text())
            data['crt_vs_period_cells'] += 1
            receipt.write_text(json.dumps(data))
            poisoned = receipt.read_bytes()
            result = subprocess.run([sys.executable, '-I', str(target / 'check_bridge.py')], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0, 'poisoned receipt accepted')
            self.assertEqual(receipt.read_bytes(), poisoned, 'poisoned evidence was overwritten')


if __name__ == '__main__':
    unittest.main()
