#!/usr/bin/env python3
"""Independently check the fixed small P327 fiber demonstration.

No solver, network, or third-party package is required. No full P327 claim.
"""
from copy import deepcopy
from fractions import Fraction
from itertools import combinations
import json
from math import gcd, prod
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from fiber import analyze, finite_bound  # noqa: E402


def _plain(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    return value


def build_receipt():
    cases = []
    for k in (1, 2, 3):
        for L in (1, 5):
            result = analyze([2, 3], L, 12, k)
            result['finite_bounds'] = [
                {'N': N, 'bound': finite_bound(N, result)}
                for N in (0, 12, 29, 30, 59, 60, 999, 1000, 10**6)
            ]
            cases.append(_plain(result))
    return {
        'schema': 'p327-multiplier-fiber-v1',
        'node': 'P327',
        'surface': 'S:gap:327:c40419c7',
        'scope': 'density-transfer lemma; no next-cell or asymptotic-record claim',
        'full_problem_solution': False,
        'formal_proof': False,
        'cases': cases,
    }


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _oracle_smooth(P, cutoff):
    found = []
    for n in range(1, cutoff + 1):
        rest = n
        for p in P:
            while rest % p == 0:
                rest //= p
        if rest == 1:
            found.append(n)
    return found


def _oracle_alpha(vertices, d, k):
    """Enumerate subsets using original divisibility, not activation moduli."""
    for size in range(len(vertices), -1, -1):
        for sub in combinations(vertices, size):
            if all(k*(d*a)*(d*b) % (d*a+d*b) != 0
                   for a,b in combinations(sub, 2)):
                return size
    raise AssertionError('the empty set must be independent')


def _period_count(X, P, L, d):
    """Second state-count algorithm: count residues, not inclusion-exclusion."""
    Q = prod(P)
    period = Q * L
    flags = [gcd(m,Q) == 1 and gcd(m,L) == d for m in range(1,period+1)]
    cycles, rest = divmod(X,period)
    return cycles * sum(flags) + sum(flags[:rest])


def negative_controls(data):
    """Mutate evidence, then call precisely the normal acceptance gate."""
    check_receipt(data)
    mutations = {
        'wrong_alpha': (('cases',1,'states',1,'alpha',2),99),
        'invented_edge': (('cases',0,'states',0,'edges',0),[1,2]),
        'wrong_weight': (('cases',1,'states',1,'weight'),'1'),
        'wrong_bound': (('cases',1,'finite_bounds',7,'bound'),0),
        'wrong_witness': (('cases',0,'states',0,'witnesses',0),[1,1]),
        'wrong_delta': (('cases',1,'states',1,'delta',0),1),
        'bool_for_integer': (('cases',0,'k'),True),
    }
    rejected = []
    for name in list(mutations) + ['missing_state','missing_case']:
        bad = deepcopy(data)
        if name == 'missing_state':
            bad['cases'][1]['states'].pop()
        elif name == 'missing_case':
            bad['cases'].pop()
        else:
            path, value = mutations[name]
            target = bad
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = value
        try:
            check_receipt(bad)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('negative control accepted: '+name)
    return rejected


def check_receipt(data):
    expected = build_receipt()
    # Canonical serialized comparison distinguishes booleans from integers and
    # rejects missing/extra cases or fields. It is not the independent oracle.
    _require(json.dumps(data,sort_keys=True) == json.dumps(expected,sort_keys=True),
             'receipt differs from exact recomputation')
    graphs = prefixes = 0
    bounds = []
    for case in data['cases']:
        P, L, k = case['P'], case['L'], case['k']
        S = _oracle_smooth(P,case['cutoff'])
        _require(S == case['smooth'], 'smooth-prefix coverage mismatch')
        coefficient = Fraction(1)
        for row in case['states']:
            d = row['d']
            actual_edges = [[a,b] for a,b in combinations(S,2)
                            if k*(d*a)*(d*b) % (d*a+d*b) == 0]
            _require(row['edges'] == actual_edges, 'edge mismatch')
            alpha = [_oracle_alpha(S[:i],d,k) for i in range(1,len(S)+1)]
            _require(row['alpha'] == alpha, 'independent-set optimum mismatch')
            deficits = [0] + [i-b for i,b in enumerate(alpha,1)]
            delta = [b-a for a,b in zip(deficits,deficits[1:])]
            _require(row['delta'] == delta, 'deficit increments mismatch')
            weight = Fraction(_period_count(prod(P)*L,P,L,d),prod(P)*L)
            _require(Fraction(row['weight']) == weight, 'state-density mismatch')
            coefficient -= weight * sum(Fraction(e,c) for e,c in zip(delta,S))
            for i,witness in enumerate(row['witnesses'],1):
                _require(len(set(witness)) == len(witness) == alpha[i-1],
                         'invalid independent-set witness cardinality')
                _require(set(witness) <= set(S[:i]), 'witness outside its prefix')
                _require(all(k*(d*a)*(d*b) % (d*a+d*b) != 0
                             for a,b in combinations(witness,2)),
                         'witness is not independent')
            graphs += 1
            prefixes += len(alpha)
        _require(coefficient == Fraction(case['coefficient']), 'density bound mismatch')
        for example in case['finite_bounds']:
            N = example['N']
            missing = sum(e*_period_count(N//c,P,L,row['d'])
                          for row in case['states'] for e,c in zip(row['delta'],S))
            _require(example['bound'] == N-missing, 'finite-N bound mismatch')
        bounds.append({'k':k, 'L':L, 'coefficient':str(coefficient)})
    return {'verdict':'PASS', 'graphs':graphs, 'prefixes':prefixes, 'bounds':bounds,
            'full_problem_solution':False, 'formal_proof':False}


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    files = parser.add_mutually_exclusive_group()
    files.add_argument('--receipt',type=Path,default=None)
    files.add_argument('--emit',type=Path,default=None,
                       help='explicitly create a new receipt; never overwrite')
    parser.add_argument('--negative-controls',action='store_true')
    args = parser.parse_args(argv)
    try:
        data = build_receipt() if args.emit else json.loads(
            (args.receipt or HERE/'receipt.json').read_text(encoding='utf-8'))
        summary = check_receipt(data)
        if args.negative_controls:
            summary['rejected_controls'] = negative_controls(data)
        if args.emit:
            with args.emit.open('x',encoding='utf-8') as stream:
                stream.write(json.dumps(data,indent=2,sort_keys=True)+'\n')
        summary['read_only'] = args.emit is None
        print(json.dumps(summary,indent=2,sort_keys=True))
        return 0
    except (ValueError,OSError) as error:
        print(json.dumps({'verdict':'FAIL','reason':str(error)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
