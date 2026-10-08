#!/usr/bin/env python3
"""Exact finite illustration of a sparse coherent interval; not an infinite-proof checker."""
import argparse
from array import array
from fractions import Fraction
import hashlib
import json
from pathlib import Path

SEED = b'efa-correlation-barrier-20261007-v1'
X, START, LENGTH = 131072, 65536, 4096
SHIFTS = [1, 2, 3, 4, 8, 16, 32]
WINDOWS = [1, 16, 64, 256, 1024]
FORMS = [(1, 0, 2, 1), (2, 1, 3, 2), (3, 0, 1, 7)]


def signs(limit):
    result = array('b', [0])  # index zero is unused
    chunk = 0
    while len(result) <= limit:
        digest = hashlib.sha256(SEED + chunk.to_bytes(8, 'big')).digest()
        result.extend(1 if byte & (1 << bit) else -1 for byte in digest for bit in range(8))
        chunk += 1
    del result[limit + 1:]
    return result


def prefix(values):
    sums = [0] * len(values)
    for n in range(1, len(values)):
        sums[n] = sums[n - 1] + values[n]
    return sums


def energy(sums, x, h):
    return sum((sums[n + h] - sums[n]) ** 2 for n in range(1, x + 1))


def checks():
    small = signs(80)
    sums = prefix(small)
    for x in [1, 3, 11, 32]:
        for h in [1, 2, 5, 13]:
            direct = sum(sum(small[n + 1:n + h + 1]) ** 2 for n in range(1, x + 1))
            assert energy(sums, x, h) == direct
    # The lower bound depends on the coherent block: reject a broken witness.
    test = array('b', [0] + [1] * 20)
    test[10] = -1
    try:
        assert all(test[n] == 1 for n in range(5, 15))
    except AssertionError:
        pass
    else:
        raise AssertionError('Planted-failure control did not fail')


def compute():
    checks()
    background = signs(3 * X + 8)
    modified = array('b', background)
    for n in range(START, START + LENGTH):
        modified[n] = 1
    assert all(modified[n] == 1 for n in range(START, START + LENGTH))
    bprefix, aprefix = prefix(background), prefix(modified)
    windows = []
    for h in WINDOWS:
        value = energy(aprefix, X, h)
        contained = LENGTH - h + 1
        lower_bound = contained * h * h
        assert contained > 0 and value >= lower_bound
        windows.append({'H': h, 'background_energy_sum': energy(bprefix, X, h),
                        'modified_energy_sum': value, 'contained_windows': contained,
                        'energy_lower_bound_sum': lower_bound,
                        'normalized_modified_energy': str(Fraction(value, X * h)),
                        'normalized_lower_bound': str(Fraction(lower_bound, X * h))})
    assert windows[-1]['modified_energy_sum'] > 24 * X * WINDOWS[-1]
    correlations = []
    for h in SHIFTS:
        old = sum(background[n] * background[n + h] for n in range(1, X + 1))
        new = sum(modified[n] * modified[n + h] for n in range(1, X + 1))
        changed_terms = sum((START <= n < START + LENGTH) or
                            (START <= n + h < START + LENGTH) for n in range(1, X + 1))
        assert abs(new - old) <= 2 * changed_terms <= 4 * LENGTH
        correlations.append({'shift': h, 'background_sum': old, 'modified_sum': new,
                             'changed_products': changed_terms})
    affine = []
    for u, v, w, z in FORMS:
        assert u * z != v * w
        old = sum(background[u * n + v] * background[w * n + z] for n in range(1, X + 1))
        new = sum(modified[u * n + v] * modified[w * n + z] for n in range(1, X + 1))
        affine.append({'forms': [u, v, w, z], 'background_sum': old, 'modified_sum': new})
    return {'schema': 'efa-finite-correlation-barrier-v1', 'problem_id': 'P969',
            'interface': 'method:fixed-window-mobius-variance',
            'claim_scope': 'One exact finite sign sequence and its measurements; no infinite-probability or Mobius claim.',
            'recipe': {'seed_utf8': SEED.decode(), 'hash': 'sha256(seed || uint64_be(chunk)); bits LSB first per byte; 0 -> -1, 1 -> +1',
                       'X': X, 'planted_start': START, 'planted_length': LENGTH,
                       'computed_prefix_length': len(modified) - 1},
            'modified_signed_byte_sha256': hashlib.sha256(modified.tobytes()).hexdigest(),
            'windows': windows, 'shift_correlations': correlations, 'affine_correlations': affine,
            'controls': {'small_direct_sum_crosscheck': 'PASS', 'broken_constant_block_rejected': True}}


def validate(expected, actual):
    if expected != actual:
        raise ValueError('Receipt does not match the reconstructed finite witness')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--emit', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    actual = compute()
    if args.emit:
        # Exclusive creation keeps a replay from silently replacing a receipt.
        with args.emit.open('x') as f:
            f.write(json.dumps(actual, indent=2) + '\n')
        print('Emitted exact finite measurements; infinite theorem not checked by this program.')
    else:
        validate(json.loads(args.check.read_text()), actual)
        bad = json.loads(json.dumps(actual))
        bad['windows'][-1]['modified_energy_sum'] += 1
        try:
            validate(bad, actual)
        except ValueError:
            pass
        else:
            raise AssertionError('Corrupted receipt accepted')
        print('PASS: exact finite witness, direct-sum checks, block lower bounds, and corrupted-receipt rejection.')
        print('At H=1024, normalized energy is ' + actual['windows'][-1]['normalized_modified_energy'] + ' (>24).')


if __name__ == '__main__':
    main()
