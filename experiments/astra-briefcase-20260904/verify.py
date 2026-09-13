#!/usr/bin/env python3
"""Recompute the transfer witnesses; never emit or overwrite evidence.

Requires the atlas checkout, including the first Astra bundle's independent
full-tree DP and the frozen small free-tree generator. Does not verify the
informal all-core proof, literature novelty, or arbitrary tree unimodality.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_all(data_dir):
    data_dir = Path(data_dir)
    tail = load('tail_oracle', HERE / 'tail.py')
    dp = load('independent_tree_dp', ROOT / 'experiments/astra-20260904/probe.py')
    ft = load('frozen_free_trees', ROOT / 'certificates/erdos-993/freetrees.py')
    records = []
    path_count = 0
    core_counts = []
    for h in range(3, 9):
        cores = list(ft.free_trees(h))
        core_counts.append(len(cores))
        saved = json.loads((data_dir / f'transfer-h{h}.json').read_text())
        expected = []
        for core_index, core in enumerate(cores):
            try:
                rec = tail.transfer(core)
            except ValueError as exc:
                assert 'path cores' in str(exc)
                path_count += 1
                continue
            assert rec['core'] == core
            parent = list(core)
            for v, count in enumerate(rec['counts']):
                for _ in range(count):
                    middle = len(parent)
                    parent.extend((v, middle))
            degrees = [0] * len(parent)
            for v, p in enumerate(parent[1:], 1):
                assert 0 <= p < v
                degrees[v] += 1
                degrees[p] += 1
            assert [v for v, d in enumerate(degrees) if d >= 3] == list(range(h))
            coeff = dp.tree_polynomial(parent)
            k = rec['index']
            assert coeff[k-1:k+2] == rec['coefficients']
            assert coeff[k]**2 - coeff[k-1]*coeff[k+1] == rec['defect'] < 0
            assert rec['order'] == len(parent)
            rec['core_index'] = core_index
            rec['full_dp_checked'] = True
            rec['full_polynomial_unimodal'] = dp.classify(coeff)['unimodal']
            rec['polynomial_sha256'] = hashlib.sha256(
                json.dumps(coeff, separators=(',', ':')).encode()).hexdigest()
            rec['polynomial_coefficients'] = coeff
            expected.append(rec)
        assert saved == expected, f'computed witness mismatch: core order {h}'
        records.extend(expected)
    assert core_counts == [1, 2, 3, 6, 11, 23], 'small free-tree count control'
    summary = {
        'compiled': len(records),
        'core_orders': sorted(set(len(r['core']) for r in records)),
        'excluded_paths': path_count,
        'min_tree_order': min(r['order'] for r in records),
        'max_tree_order': max(r['order'] for r in records),
        'all_lc_failures_verified': all(r['full_dp_checked'] and r['defect'] < 0 for r in records),
        'unimodal_true': sum(r['full_polynomial_unimodal'] for r in records),
        'N_distribution': {str(k): v for k, v in Counter(r['N'] for r in records).items()},
        'scope': 'all non-path unlabelled tree cores in orders3..8, via frozen generator; NOT exhaustive decorated trees'
    }
    assert summary == json.loads((data_dir / 'transfer-summary.json').read_text())
    large = json.loads((data_dir / 'million-vertex-tail.json').read_text())
    top = tail.tail_coefficients(large['core_parent'], large['arm_counts'], large['depth'])
    assert [hex(x) for x in top] == large['coefficient_hex']
    assert [x.bit_length() for x in top] == large['coefficient_bit_lengths']
    assert large['tree_order'] == len(large['core_parent']) + 2*sum(large['arm_counts'])
    # Recorded wall-clock timing is observational and deliberately not a gate.
    return {'verified': True, 'compiled_cores': len(records),
            'unimodal_witnesses': summary['unimodal_true'],
            'large_tree_order': large['tree_order'], 'large_tail_depth': len(top),
            'scope': 'finite witnesses and exact tails only; not an Erdos 993 solution'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=HERE)
    args = parser.parse_args()
    print(json.dumps(verify_all(args.data_dir), indent=2))
