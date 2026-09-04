"""Exact integer tools for P993. No dependency or floating arithmetic."""


def add(a, b):
    c = [0] * max(len(a), len(b))
    for i, v in enumerate(a):
        c[i] += v
    for i, v in enumerate(b):
        c[i] += v
    return c


def mul(a, b):
    c = [0] * (len(a) + len(b) - 1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            c[i + j] += u * v
    return c


def tree_polynomial(parent):
    """Parents are topologically ordered; -1 at root. Empty forest gives 1."""
    if not parent:
        return [1]
    if parent[0] != -1 or any(not 0 <= parent[i] < i for i in range(1, len(parent))):
        raise ValueError('expected a topologically ordered tree parent array')
    excluded = [[1] for _ in parent]
    included = [[0, 1] for _ in parent]
    for v in range(len(parent) - 1, 0, -1):
        p = parent[v]
        excluded[p] = mul(excluded[p], add(excluded[v], included[v]))
        included[p] = mul(included[p], excluded[v])
    return add(excluded[0], included[0])


def hub_path(arms, joins):
    """A path of hubs, pendant arm edge lengths and connector edge lengths."""
    if not arms or len(joins) != len(arms) - 1:
        raise ValueError('one connector between consecutive hubs')
    if any(x < 1 for x in joins) or any(x < 1 for a in arms for x in a):
        raise ValueError('all paths have positive edge length')
    parent, hubs = [-1], [0]
    for length in joins:
        v = hubs[-1]
        for _ in range(length):
            parent.append(v)
            v = len(parent) - 1
        hubs.append(v)
    for hub, paths in zip(hubs, arms):
        for length in paths:
            v = hub
            for _ in range(length):
                parent.append(v)
                v = len(parent) - 1
    return parent


def classify(a):
    breaks = [i for i in range(1, len(a) - 1) if a[i] ** 2 < a[i - 1] * a[i + 1]]
    falling = False
    rises = []
    for i in range(1, len(a)):
        if a[i] < a[i - 1]:
            falling = True
        elif a[i] > a[i - 1] and falling:
            rises.append(i)
    return {'log_concave': not breaks, 'lc_breaks': breaks,
            'unimodal': not rises, 'rises_after_fall': rises}


def run_search(initial_samples=1500, samples_per_hub=5000):
    """Reproduce the exploratory samples, not an exhaustive search."""
    import hashlib
    import json
    import random
    seed = 99320260904
    rng = random.Random(seed)
    digest = hashlib.sha256()
    batches, failures, seen = [], [], set()
    configs = [(3, initial_samples, 14, [1, 2, 2, 2, 3, 4, 5, 6], 7)]
    configs += [(h, samples_per_hub, 18, [1, 2, 2, 2, 2, 3, 4, 7], 6)
                for h in (3, 4, 5, 8)]
    for hubs, count, maximum, choices, connector_max in configs:
        orders = []
        bad_lc = bad_uni = 0
        for _ in range(count):
            arms = tuple(tuple(sorted(rng.choices(choices, k=rng.randint(
                2 if j in (0, hubs - 1) else 1, maximum)))) for j in range(hubs))
            joins = tuple(rng.randint(1, connector_max) for _ in range(hubs - 1))
            parent = hub_path(arms, joins)
            coeff = tree_polynomial(parent)
            state = classify(coeff)
            canonical = min((arms, joins), (arms[::-1], joins[::-1]))
            seen.add(canonical)
            digest.update((json.dumps([canonical, coeff], separators=(',', ':')) + '\n').encode())
            orders.append(len(parent))
            bad_lc += not state['log_concave']
            bad_uni += not state['unimodal']
            if not state['log_concave']:
                failures.append({'arms': arms, 'joins': joins, 'parent': parent,
                                 'coefficients': coeff, **state})
        batches.append({'hubs': hubs, 'samples': count, 'min_order': min(orders),
                        'max_order': max(orders), 'lc_failures': bad_lc,
                        'unimodality_failures': bad_uni})
    return {'problem': 'P993', 'surface': 'S:triage:993',
            'status': 'exploratory finite samples; no theorem or frontier promotion',
            'seed': seed, 'samples': sum(b['samples'] for b in batches),
            'distinct_trees': len(seen), 'batches': batches,
            'log_concavity_failures': sum(b['lc_failures'] for b in batches),
            'unimodality_failures': sum(b['unimodality_failures'] for b in batches),
            'stream_sha256': digest.hexdigest(), 'failures': failures}


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='write a NEW local experiment receipt')
    args = parser.parse_args()
    result = run_search()
    target = Path(__file__).with_name('RESULT.json')
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.emit:
        # Exclusive creation: an existing proof object is never overwritten.
        with target.open('x') as f:
            f.write(payload)
    elif not target.exists() or target.read_text() != payload:
        raise SystemExit('FAIL: receipt differs from complete recomputation')
    print(payload)
