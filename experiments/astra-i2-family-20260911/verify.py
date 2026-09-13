#!/usr/bin/env python3
"""Recompute the i=2 family witnesses. Never overwrite evidence."""
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_i2():
    spec = importlib.util.spec_from_file_location('i2', HERE / 'i2.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    i2 = load_i2()
    records = [i2.erdos699_i2_witness(j) for j in range(3, 401)]
    assert all(r['m'] >= 3 and r['prime'] >= 3 for r in records)
    assert all(math.comb(r['n'], 2) % r['m'] == 0 for r in records)
    assert all(math.comb(r['n'], r['j']) % r['m'] == 0 for r in records)
    rec12 = i2.erdos699_i2_witness(12)
    assert rec12['m'] == 9 and rec12['prime'] == 3
    out = {
        'verified': True,
        'j_min': 3,
        'j_max': 400,
        'count': len(records),
        'composite_m_example': rec12,
        'scope': 'finite exact checks of the i=2, n=2j+3 family; not full P699',
    }
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
