#!/usr/bin/env python3
"""Independent adversarial review; stdlib and exact integer arithmetic only.
No imports from check.py. Reads its JSON replay and verifies each printed base.
"""
import argparse
import itertools
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def add(*polys):
    out = Counter()
    for p in polys:
        for k, v in p.items():
            out[k] += v
    return {k: v for k, v in out.items() if v}


def times(a, b):
    out = Counter()
    for i, u in a.items():
        for j, v in b.items():
            out[i + j] += u * v
    return dict(out)


def product(*polys):
    out = {0: 1}
    for p in polys:
        out = times(out, p)
    return out


def scaled(p, n):
    return {k: n * v for k, v in p.items() if n * v}


def power(n):
    out = {0: 1}
    for _ in range(n):
        out = times(out, {-1: 1, 1: 1})
    return out


def pair(n):
    return dict(Counter((n, -n)))


def check_cu(p, n):
    assert p and max(p) <= n and min(p) >= -n
    assert all(v >= 0 and (k - n) % 2 == 0 for k, v in p.items())
    assert all(p.get(k, 0) == p.get(-k, 0) for k in range(-n, n + 1))
    row = [p.get(k, 0) for k in range(n, -1, -2)]
    ds = [b - a for a, b in zip(row, row[1:])]
    assert all(d >= 0 for d in ds), (n, p, ds)
    return ds


def direct_states(rs):
    """Enumerate inactive w factors and signs of active runs directly."""
    result = Counter()
    for mask in itertools.product((False, True), repeat=3):
        # Each free w factor independently contributes +/-1.
        free = sum(n for n, active in zip(rs, mask) if not active)
        runs = []
        pos = 0
        while pos < 3:
            if not mask[pos]:
                pos += 1
                continue
            alt, sign = 0, 1
            while pos < 3 and mask[pos]:
                alt += sign * rs[pos]
                sign = -sign
                pos += 1
            runs.append(alt)
        for choices in itertools.product((-1, 1), repeat=free + len(runs)):
            exponent = sum(choices[:free]) + sum(
                a * b for a, b in zip(choices[free:], runs)
            )
            result[exponent] += 1
    return dict(result)


# Sparse symbolic Laurent ring in x,y,z,A,B,T,C,D,E, where
# x=z_original^r, y=z_original^s, z=z_original^t, A=W_r, B=W_s,
# T=W_t. C,D,E are the shifted scalar variables. Treating the six
# underlying symbols as independent proves a stronger formal identity.
ZERO = (0,) * 9
ONE = {ZERO: 1}


def monomial(index, exponent=1):
    key = list(ZERO)
    key[index] = exponent
    return {tuple(key): 1}


def smul(*polys):
    out = ONE
    for p in polys:
        nxt = Counter()
        for k, a in out.items():
            for l, b in p.items():
                nxt[tuple(u + v for u, v in zip(k, l))] += a * b
        out = {k: v for k, v in nxt.items() if v}
    return out


def spair(*xyz):
    positive = tuple(xyz) + (0,) * 6
    negative = tuple(-v for v in xyz) + (0,) * 6
    return add({positive: 1}, {negative: 1})


def symbolic_identity():
    A, B, T, C, D, E = (monomial(i) for i in range(3, 9))
    c, d, e = (add(ONE, x) for x in (C, D, E))
    xs = [A, B, T]
    cs = [c, d, e]
    state_terms = []
    unit_terms = []
    for mask in itertools.product((False, True), repeat=3):
        weighted, unit = [], []
        pos = 0
        while pos < 3:
            if not mask[pos]:
                weighted.append(smul(xs[pos], cs[pos]))
                unit.append(xs[pos])
                pos += 1
            else:
                v, sign = [0, 0, 0], 1
                while pos < 3 and mask[pos]:
                    v[pos] = sign
                    sign = -sign
                    pos += 1
                p = spair(*v)
                weighted.append(p)
                unit.append(p)
        state_terms.append(smul(*weighted))
        unit_terms.append(smul(*unit))
    Qr, Qs, Qt = add(A, spair(1, 0, 0)), add(B, spair(0, 1, 0)), add(T, spair(0, 0, 1))
    Hst = add(smul(Qs, Qt), scaled(spair(0, 1, 1), -1))
    Hrs = add(smul(Qr, Qs), scaled(spair(1, 1, 0), -1))
    shifted = add(add(*unit_terms), smul(C, A, Hst), smul(D, B, Qr, Qt),
                  smul(E, T, Hrs), smul(C, D, A, B, Qt),
                  smul(C, E, A, T, Qs), smul(D, E, B, T, Qr),
                  smul(C, D, E, A, B, T))
    direct = add(*state_terms)
    assert direct == shifted
    return len(direct)


def parse_table(text, header=None):
    """Consume every line as whitespace-separated, complete integer entries."""
    lines = text.strip().splitlines()
    if header is not None:
        if not lines or lines.pop(0).strip() != header:
            raise ValueError('Malformed displayed table header')
    entry = re.compile(r'\(([0-9]+(?:,[0-9]+)*)\):\s*'
                       r'([0-9]+(?:,[0-9]+)*)(?=\s|$)')
    table = {}
    for line in lines:
        remaining = line.strip()
        while remaining:
            match = entry.match(remaining)
            if match is None:
                raise ValueError(f'Malformed displayed table entry: {remaining!r}')
            key = tuple(map(int, match[1].split(',')))
            if key in table:
                raise ValueError(f'Duplicate displayed table entry: {key}')
            table[key] = list(map(int, match[2].split(',')))
            remaining = remaining[match.end():].lstrip()
    return table


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--replay-bound', type=int, default=24)
    args = ap.parse_args()
    if args.replay_bound < 1:
        ap.error('--replay-bound must be positive')
    replay = json.loads(subprocess.check_output(
        [sys.executable, '-I', str(ROOT / 'check.py'), '--bound', str(args.replay_bound)],
        text=True))
    assert replay['checked'] == args.replay_bound ** 3
    assert replay['status'] == 'PASS' and not replay['counterexamples']
    receipt = json.loads((ROOT / 'receipt.json').read_text())
    common_keys = set(replay) - {'checked', 'bound', 'counterexamples', 'tight'}
    assert all(replay[key] == receipt[key] for key in common_keys)
    full_receipt_match = replay == receipt
    if args.replay_bound == receipt['bound']:
        assert full_receipt_match
    groups = replay['proof']
    expected_single = {(a, b) for a in range(1, 8) for b in range(8)
                       if a + b <= 7 and (7 - a - b) % 2 == 0}
    expected_double = {rs for rs in itertools.product(range(1, 8), repeat=3)
                       if sum(rs) == 7}
    expected_small = {rs for rs in itertools.product(range(1, 7), repeat=3)
                      if 3 <= sum(rs) <= 6}
    observed_single = {(x['a'], x['b']) for x in groups['single_boundary']}
    observed_double = {(x['r'], x['s'], x['t']) for x in groups['double_boundary']}
    observed_small = {(x['r'], x['s'], x['t']) for x in groups['small_blocks']}
    for expected, observed, key in (
            (expected_single, observed_single, 'single_boundary'),
            (expected_double, observed_double, 'double_boundary'),
            (expected_small, observed_small, 'small_blocks')):
        assert expected == observed and len(expected) == len(groups[key])

    # Parse all three displayed tables; catch stale, mistyped or omitted entries.
    text = (ROOT / 'RESULT.md').read_text()
    small_intro = 'differences, calculated directly from the eight-state definition, are:'
    spans = [(text.rfind('\n', 0, text.index('(a,b): differences')) + 1,
              text.index('This closes the induction.'), '(a,b): differences'),
             (text.rfind('\n', 0, text.index('(r,s,t): differences')) + 1,
              text.index('**Isolated-P lemma.**'), '(r,s,t): differences'),
             (text.index(small_intro) + len(small_intro),
              text.index('Thus the unit-scalar result'), None)]
    for (lo, hi, header), key in zip(spans, ('single_boundary', 'double_boundary', 'small_blocks')):
        table = parse_table(text[lo:hi], header)
        records = groups[key]
        expected = {tuple(x[k] for k in (('a', 'b') if key == 'single_boundary' else ('r', 's', 't'))): x['differences'] for x in records}
        assert table == expected

    for x in groups['single_boundary']:
        p = add(power(7), scaled(product(power(x['a']), pair(x['b'])), 7))
        assert check_cu(p, 7) == x['differences']
    for x in groups['double_boundary']:
        p = add(power(7), scaled(product(power(x['s']), pair(x['r']), pair(x['t'])), 7))
        assert check_cu(p, 7) == x['differences']
    for x in groups['small_blocks']:
        rs = x['r'], x['s'], x['t']
        assert check_cu(direct_states(rs), sum(rs)) == x['differences']

    # Diagnostic tests of the infinite-boundary coefficient assertions.
    base_single = base_double = margin_rows = 0
    for n in range(7, 101):
        w = power(n)
        diffs = check_cu(w, n)
        assert min(diffs[1:]) >= 14
        margin_rows += 1
        for b in range(2, n):
            if (n - 1 - b) % 2:
                continue
            p = product(power(1), pair(b))
            assert max(p.values()) <= 1
            assert p.get(n - 2, 0) >= p.get(n, 0)
            check_cu(add(w, scaled(p, 7)), n)
            base_single += 1
        for r in range(1, n - 1):
            t = n - 1 - r
            p = product(power(1), pair(r), pair(t))
            assert max(p.values()) <= 2
            assert p[n] == 1 and p[n - 2] in (1, 2)
            check_cu(add(w, scaled(p, 7)), n)
            base_double += 1
    formal_terms = symbolic_identity()
    print(json.dumps({'status': 'PASS', 'replayed_blocks': replay['checked'],
                      'receipt_matches_replay': full_receipt_match,
                      'independent_base_counts': [len(expected_single), len(expected_double), len(expected_small)],
                      'printed_tables_match': True, 'symbolic_shift_identity_terms': formal_terms,
                      'diagnostic_margin_rows': margin_rows,
                      'diagnostic_a1_single_cases': base_single,
                      'diagnostic_s1_double_cases': base_double}, indent=2))


if __name__ == '__main__':
    main()
