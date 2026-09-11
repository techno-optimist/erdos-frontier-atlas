#!/usr/bin/env python3
"""Recompute i=2 complete-case witnesses. Never overwrite evidence."""
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from i2all import gcd_both, identity, binom2_gt


def main():
    count = 0
    for n in range(6, 81):
        for j in range(3, n // 2 + 1):
            assert identity(n, j) == 0
            assert binom2_gt(n, j)
            assert gcd_both(n, j) >= 2
            count += 1
    rec = {
        'verified': True,
        'n_min': 6,
        'n_max': 80,
        'pairs': count,
        'smallest': {'n': 6, 'j': 3, 'gcd': gcd_both(6, 3)},
        'scope': 'complete i=2 slice of P699 in gcd form; not full P699',
    }
    print(json.dumps(rec, indent=2))


if __name__ == '__main__':
    main()
