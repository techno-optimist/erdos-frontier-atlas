"""Exact top coefficients of trees with pendant P2 bundles.

An arithmetic reduction, not a proof of log-concavity or unimodality.
For core H and t_v arms, I_T(x) = sum_S x^|S| (1+x)^t(S)
                                           (1+2x)^(sum(t)-t(S)),
where S ranges over independent sets of H.
"""
from collections import Counter
from functools import lru_cache
from math import comb


@lru_cache(maxsize=None)
def independent_sets(parent):
    return tuple(tuple(v for v in range(len(parent)) if mask & (1 << v))
                 for mask in range(1 << len(parent))
                 if all(not (mask & (1 << v) and mask & (1 << parent[v]))
                        for v in range(1, len(parent))))


def tail_coefficients(parent, counts, depth):
    """Return coefficients from highest degree downward, at most depth.

    Arithmetic operation count depends on core size and requested depth,
    not the number of arms. Integer bit complexity DOES depend on arm count.
    Core vertices must be topologically ordered: parent[0]=-1, 0<=parent[v]<v.
    """
    parent = tuple(parent)
    if not parent or parent[0] != -1 or any(type(p) is not int or not 0 <= p < v
                                           for v, p in enumerate(parent[1:], 1)):
        raise ValueError('expected a nonempty topologically ordered core tree')
    if len(counts) != len(parent) or any(type(t) is not int or t < 0 for t in counts):
        raise ValueError('one nonnegative integer arm count per core vertex required')
    if type(depth) is not int or depth < 1:
        raise ValueError('positive integer depth required')
    sets = independent_sets(parent)
    alpha = max(map(len, sets))
    total = sum(counts)
    groups = Counter((len(s), sum(counts[v] for v in s)) for s in sets)
    out = [0] * min(depth, total + alpha + 1)
    for (size, selected), multiplicity in groups.items():
        other = total - selected
        offset = alpha - size
        for r in range(offset, len(out)):
            q = r - offset
            coefficient = 0
            for a in range(max(0, q - other), min(q, selected) + 1):
                b = q - a
                coefficient += comb(selected, a) * comb(other, b) * (1 << (other - b))
            out[r] += multiplicity * coefficient
    return tuple(out)


def transfer(parent, max_rounds=16):
    """Construct a non-log-concave P2 decoration of a non-path core tree.

    The theorem proves eventual success, not this implementation's budget.
    A budget exhaustion raises rather than masquerading as a negative result.
    """
    from fractions import Fraction
    from math import prod

    parent = tuple(parent)
    tail_coefficients(parent, [0] * len(parent), 1)  # validate core
    if type(max_rounds) is not int or max_rounds < 1:
        raise ValueError('positive integer max_rounds required')
    adj = [[] for _ in parent]
    for v, p in enumerate(parent[1:], 1):
        adj[v].append(p)
        adj[p].append(v)
    center = next((v for v, neighbors in enumerate(adj) if len(neighbors) >= 3), None)
    if center is None:
        raise ValueError('path cores have no claw; no obstruction is asserted')
    leaves = adj[center][:3]
    h = len(parent)
    B = (256 * comb(h, 2) - 1).bit_length()
    offsets = [0 if v == center else 3 if v in leaves else B for v in range(h)]
    sets = independent_sets(parent)
    alpha = max(map(len, sets))
    weights = [Fraction(1, 1 << b) for b in offsets]
    f = [sum((prod(weights[v] for v in s) for s in sets if len(s) == k), Fraction())
         for k in (1, 2, 3)]
    weighted_defect = f[1]**2 - f[0]*f[2]
    if weighted_defect > Fraction(-7, 65536):
        raise ArithmeticError('weighted perturbation bound failed')
    attempts = []
    for iteration in range(max_rounds):
        N = 1 << iteration
        counts = [N + b for b in offsets]
        top = tail_coefficients(parent, counts, alpha)
        a, b, c = top[alpha - 1], top[alpha - 2], top[alpha - 3]
        defect = b*b - a*c
        attempts.append({'N': N, 'defect_negative': defect < 0})
        if defect < 0:
            return {'core': list(parent), 'claw': [center] + leaves,
                    'offsets': offsets, 'counts': counts, 'N': N,
                    'order': h + 2*sum(counts), 'index': sum(counts) + 2,
                    'coefficients': [a, b, c], 'defect': defect,
                    'weighted_coefficients': [str(x) for x in f],
                    'weighted_defect': str(weighted_defect), 'attempts': attempts,
                    'scope': 'non-log-concavity only; unimodality not decided here'}
    raise RuntimeError('search budget exhausted; no nonexistence claim')
