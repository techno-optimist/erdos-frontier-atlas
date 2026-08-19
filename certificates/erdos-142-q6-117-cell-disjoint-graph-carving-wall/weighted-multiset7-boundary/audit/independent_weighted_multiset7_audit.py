#!/usr/bin/env python3
"""Independent hostile audit of the weighted multiset-7 sunflower packet.

This file imports no source-packet module.  It uses alternative finite
representations for the literal multiset seam, the LYM LP dual, and the DFA
product quotient.  Only Python's standard library is required.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
from math import comb
from pathlib import Path

SOURCE_NAME = "erdos142_weighted_multiset7_sunflower_20260819"
SOURCE_HASHES = {
    "README.md": "9313303477481dd313f96532750a07f0cdb06f6abee3276fec4028f099797045",
    "THEOREM.md": "37e9674e49d5fbeb3793cd2a21c06797082d8027c0b4ff2a63103020cf2a8692",
    "FINITE_STATE.md": "431307c1bc4463988ec7cd4d3f6d585237f7eeac98ed35e5347fc48b43cd7534",
    "verify_weighted_multiset7.py": "10e584bc7974ae2216bd1dd9d004e50ed12d9146c3c45a580ad632eaf3374775",
    "finite_state_explorer.py": "1d221fc9c847616708e24f8cf80f6557150c606f3326a891e56f3b29a9a1d89e",
    "run.ps1": "40808472fd211a4435f087de96b7471d7c3d247ad83b033a2a8a92282b29d2a0",
    "SHA256SUMS": "c54c33d95df9979be73b683d42af4ab858c7791684252fba808b56bfa0c87f22",
}

B = 263_277
R = 17_640
G = Fraction(1_058_841, 4)
X = Fraction(R, B)
Y = G / B


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def source_snapshot():
    source = Path(__file__).resolve().parent.parent / SOURCE_NAME
    files = {path.name for path in source.iterdir() if path.is_file()}
    need(files == set(SOURCE_HASHES), "source payload file census changed")
    actual = {name: sha256((source / name).read_bytes()).hexdigest()
              for name in sorted(files)}
    need(actual == SOURCE_HASHES, "source packet hash mismatch")
    return actual


def literal_bad(septuple, dimension):
    saw_unit = False
    for coordinate in range(dimension):
        weight = sum((word >> coordinate) & 1 for word in septuple)
        if weight not in (0, 1, 7):
            return False
        saw_unit |= weight == 1
    return saw_unit


def proper_subset(a, b):
    return a != b and a & ~b == 0


def comparable(supports):
    return any(proper_subset(a, b) or proper_subset(b, a)
               for a, b in combinations(supports, 2))


def distinct_sunflower(seven, dimension):
    return len(set(seven)) == 7 and literal_bad(seven, dimension)


def reduced_safe(family, dimension):
    if comparable(family):
        return False
    return not any(distinct_sunflower(seven, dimension)
                   for seven in combinations(family, 7))


def weighted_mass(family):
    return sum((X**word.bit_count() for word in family), Fraction(0))


def verify_multiset_equivalence():
    dimension = 4
    required_support_masks = set()
    bad = repeated_bad = distinct_bad = 0
    total = 0
    support_size_histogram = Counter()
    for septuple in combinations_with_replacement(range(1 << dimension), 7):
        total += 1
        if not literal_bad(septuple, dimension):
            continue
        bad += 1
        supports = tuple(sorted(set(septuple)))
        required_support_masks.add(sum(1 << word for word in supports))
        support_size_histogram[len(supports)] += 1
        if len(supports) < 7:
            repeated_bad += 1
            need(comparable(supports), "repeated forbidden multiset escaped inclusion")
        else:
            distinct_bad += 1
            need(distinct_sunflower(supports, dimension),
                 "distinct forbidden multiset is not a sunflower")
    need(total == comb(22, 7) == 170_544, "four-cube multiset census")
    need((bad, repeated_bad, distinct_bad, len(required_support_masks))
         == (135, 135, 0, 135), "four-cube forbidden census")
    need(support_size_histogram == Counter({2: 65, 3: 55, 4: 14, 5: 1}),
         "forbidden support-size census")

    # Exhaust all 65,536 families by containment of a directly enumerated
    # forbidden multiset, independently of the reduced test.
    safe_count = 0
    universe = tuple(range(1 << dimension))
    for selector in range(1 << len(universe)):
        literal_unsafe = any(required & ~selector == 0
                             for required in required_support_masks)
        family = tuple(word for word in universe if selector >> word & 1)
        structural_unsafe = not reduced_safe(family, dimension)
        need(literal_unsafe == structural_unsafe,
             "family-level multiset reduction mismatch")
        safe_count += not literal_unsafe
    need(safe_count == 168, "Dedekind d=4 antichain census")

    comparable_pairs = 0
    for a in universe:
        for b in universe:
            if proper_subset(a, b):
                comparable_pairs += 1
                need(literal_bad((a,)*6+(b,), dimension),
                     "six-plus-one inclusion witness")
    need(comparable_pairs == 3**dimension-2**dimension == 65,
         "proper inclusion pair census")
    singletons = tuple(1 << coordinate for coordinate in range(7))
    need(distinct_sunflower(singletons, 7), "ordinary sunflower control")
    need(reduced_safe(singletons[:6], 6), "six-petal control")
    return support_size_histogram


def all_reduced_safe_families(dimension):
    universe = tuple(range(1 << dimension))
    for selector in range(1 << len(universe)):
        family = tuple(word for word in universe if selector >> word & 1)
        if reduced_safe(family, dimension):
            yield family


def tensor(left, left_dimension, right):
    return tuple(a | (b << left_dimension) for a in left for b in right)


def verify_tensor_and_uniformization_algebra():
    safe = tuple(all_reduced_safe_families(3))
    need(len(safe) == 20, "three-cube safe family count")
    tested = 0
    for left in safe:
        for right in safe:
            combined = tensor(left, 3, right)
            need(reduced_safe(combined, 6), "tensor closure failure")
            need(weighted_mass(combined)
                 == weighted_mass(left)*weighted_mass(right),
                 "tensor mass failure")
            tested += 1
    need(tested == 400, "tensor pair census")
    need(X == Fraction(40, 597) and 1/X == Fraction(597, 40),
         "uniformization base")
    need(Y == Fraction(2401, 2388) and Y > 1, "gate ratio")


def two_k7_edges():
    return tuple((u, v) for offset in (0, 7)
                 for u, v in combinations(range(offset, offset+7), 2))


def matching_number(edges, vertices):
    neighbors = [0]*vertices
    for u, v in edges:
        neighbors[u] |= 1 << v
        neighbors[v] |= 1 << u
    memo = {0: 0}

    def solve(available):
        if available in memo:
            return memo[available]
        first = available & -available
        vertex = first.bit_length()-1
        rest = available ^ first
        answer = solve(rest)
        choices = neighbors[vertex] & rest
        while choices:
            partner = choices & -choices
            choices ^= partner
            answer = max(answer, 1+solve(rest ^ partner))
        memo[available] = answer
        return answer

    return solve((1 << vertices)-1)


def uniform_cap(rank):
    need(rank >= 1, "positive rank required")
    if rank == 1:
        return 6
    cap = 42
    for k in range(3, rank+1):
        cap = 6*(k*cap-(k-1))
    return cap


def verify_uniform_extrema_and_recursion():
    need(uniform_cap(1) == 6, "M1")
    edges = two_k7_edges()
    degrees = Counter()
    for u, v in edges:
        degrees[u] += 1
        degrees[v] += 1
    need(len(edges) == 42 and set(degrees.values()) == {6}, "2K7 degree witness")
    need(matching_number(edges, 14) == 6, "2K7 matching witness")
    need(42*X**2 < 1, "2K7 weighted mass")

    expected = (6, 42, 744, 17_838, 535_116, 19_264_146)
    need(tuple(uniform_cap(k) for k in range(1, 7)) == expected,
         "strengthened recursion values")
    for k in range(3, 20):
        previous = uniform_cap(k-1)
        strengthened = 6*(k*previous-(k-1))
        need(strengthened < 6*k*previous, "strict recursion improvement")
        need(all(m*(k*previous-(k-1)) <= strengthened for m in range(7)),
             "maximal-matching m bound")
    need(6*X == Fraction(240, 597) < 1, "six-cone mass factor")


def lp_primal_dual(dimension):
    items = []
    for rank in range(1, dimension+1):
        layer = comb(dimension, rank)
        cap = Fraction(min(layer, uniform_cap(rank)), layer)
        density = layer*X**rank
        items.append((density, rank, cap))

    remaining = Fraction(1)
    primal = Fraction(0)
    allocation = []
    for density, rank, cap in sorted(items, reverse=True):
        take = min(remaining, cap)
        if take:
            allocation.append((rank, take, density))
            primal += take*density
            remaining -= take
        if remaining == 0:
            break
    need(remaining == 0, "LYM unit was not filled")

    # Independent exact LP dual: lambda + sum cap_k*(density_k-lambda)_+.
    dual_candidates = []
    for threshold in {Fraction(0)} | {density for density, _, _ in items}:
        objective = threshold + sum(
            (cap*max(Fraction(0), density-threshold)
             for density, _, cap in items), Fraction(0))
        dual_candidates.append((objective, threshold))
    dual, threshold = min(dual_candidates)
    need(primal == dual, "fractional knapsack primal/dual gap")
    return primal, threshold, tuple(allocation)


def verify_exact_lym_lp():
    bounds = {dimension: lp_primal_dual(dimension)[0]
              for dimension in range(1, 41)}
    need(all(bounds[d] < 1 for d in range(1, 29)), "mass cap through d=28")
    need(bounds[29] > 1, "mass relaxation seam d=29")
    need(all(bounds[d] < Y**d for d in range(1, 32)),
         "gate cap through d=31")
    need(bounds[32] > Y**32, "gate relaxation seam d=32")
    need(min(d for d in bounds if bounds[d] > 1) == 29,
         "first mass relaxation failure")
    need(min(d for d in bounds if bounds[d] > Y**d) == 32,
         "first gate relaxation failure")
    need(bounds[28] == Fraction(126_899_718_320, 127_027_375_281),
         "exact d28 LP")
    need(bounds[29] == Fraction(44_332_119_440, 42_342_458_427),
         "exact d29 LP")
    need(bounds[31] == Fraction(16_421_746_480, 14_114_152_809),
         "exact d31 LP")
    need(bounds[32] == Fraction(90_704_272_317_040, 75_835_343_042_757),
         "exact d32 LP")
    need(bounds[28] < 1 < bounds[29] < Y**29, "mass seam signs")
    need(bounds[31] < Y**31 < bounds[32], "gate seam signs")
    # The seam allocations are fractional LP points, not set families.
    for dimension in (29, 32):
        _, _, allocation = lp_primal_dual(dimension)
        need(any(take.denominator != 1 for _, take, _ in allocation),
             "relaxation seam accidentally integral")
    return {d: bounds[d] for d in (28, 29, 31, 32)}


def push_counts(counts, delta, selected=None):
    image = [0]*len(delta)
    for state, multiplicity in enumerate(counts):
        if selected == state:
            need(multiplicity > 0, "selected absent state")
            image[delta[state][1]] += 1
            image[delta[state][0]] += multiplicity-1
        else:
            image[delta[state][0]] += multiplicity
    return tuple(image)


def globally_safe_counts(delta, accepting_mask):
    """Count-vector quotient of seven synchronized copies."""
    start_counts = (7,)+(0,)*(len(delta)-1)
    start = (start_counts, False)
    queue = deque([start])
    seen = {start}
    while queue:
        counts, active = queue.popleft()
        if active and all(not multiplicity or accepting_mask >> state & 1
                          for state, multiplicity in enumerate(counts)):
            return False
        successors = {(push_counts(counts, delta), active)}
        # Constant-one column.
        one_image = [0]*len(delta)
        for state, multiplicity in enumerate(counts):
            one_image[delta[state][1]] += multiplicity
        successors.add((tuple(one_image), active))
        # Unit columns, one representative for each occupied source state.
        for state, multiplicity in enumerate(counts):
            if multiplicity:
                successors.add((push_counts(counts, delta, state), True))
        for nxt in successors:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return True


def globally_safe_ordered(delta, accepting_mask):
    start = ((0,)*7, False)
    queue = deque([start])
    seen = {start}
    columns = ((0,)*7, (1,)*7) + tuple(
        tuple(int(i == chosen) for i in range(7)) for chosen in range(7))
    while queue:
        states, active = queue.popleft()
        if active and all(accepting_mask >> state & 1 for state in states):
            return False
        for column in columns:
            image = tuple(delta[state][bit]
                          for state, bit in zip(states, column))
            nxt = (image, active or sum(column) == 1)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return True


def reachable_states(delta):
    seen = {0}
    queue = deque([0])
    while queue:
        state = queue.popleft()
        for target in delta[state]:
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return tuple(sorted(seen))


def canonical_minimal(delta, accepting_mask):
    """Table-filling minimization followed by canonical BFS renaming."""
    reachable = reachable_states(delta)
    pairs = tuple(combinations(reachable, 2))
    distinguished = {pair for pair in pairs
                     if bool(accepting_mask >> pair[0] & 1)
                     != bool(accepting_mask >> pair[1] & 1)}

    def pair_key(a, b):
        return (a, b) if a < b else (b, a)

    changed = True
    while changed:
        changed = False
        for pair in pairs:
            if pair in distinguished:
                continue
            a, b = pair
            if any(delta[a][bit] != delta[b][bit]
                   and pair_key(delta[a][bit], delta[b][bit]) in distinguished
                   for bit in (0, 1)):
                distinguished.add(pair)
                changed = True

    unassigned = set(reachable)
    classes = []
    while unassigned:
        representative = min(unassigned)
        equivalent = {state for state in unassigned
                      if state == representative
                      or pair_key(state, representative) not in distinguished}
        classes.append(tuple(sorted(equivalent)))
        unassigned -= equivalent
    owner = {state: index for index, block in enumerate(classes) for state in block}
    quotient = tuple(tuple(owner[delta[block[0]][bit]] for bit in (0, 1))
                     for block in classes)
    qaccept = {owner[state] for state in reachable
               if accepting_mask >> state & 1}

    start = owner[0]
    number = {start: 0}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        for target in quotient[state]:
            if target not in number:
                number[target] = len(number)
                queue.append(target)
    canonical_delta = [None]*len(number)
    for old, new in number.items():
        canonical_delta[new] = tuple(number[target]
                                     for target in quotient[old])
    canonical_accept = tuple(sorted(number[state] for state in qaccept))
    return tuple(canonical_delta), canonical_accept


def weighted_matrix(delta):
    matrix = [[Fraction(0) for _ in delta] for _ in delta]
    for state in range(len(delta)):
        matrix[state][delta[state][0]] += 1
        matrix[state][delta[state][1]] += X
    return tuple(tuple(row) for row in matrix)


def weighted_sequence(delta, accepting, horizon):
    vector = [Fraction(0) for _ in delta]
    vector[0] = 1
    answer = []
    for _ in range(horizon+1):
        answer.append(sum((vector[state] for state in accepting), Fraction(0)))
        nxt = [Fraction(0) for _ in delta]
        for state, value in enumerate(vector):
            nxt[delta[state][0]] += value
            nxt[delta[state][1]] += X*value
        vector = nxt
    return tuple(answer)


def characteristic(matrix):
    size = len(matrix)
    if size == 1:
        return (-matrix[0][0], Fraction(1))
    if size == 2:
        a, b = matrix[0]
        c, d = matrix[1]
        return (a*d-b*c, -(a+d), Fraction(1))
    need(size == 3, "characteristic dimension")
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    determinant = a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)
    principal_two = a*e-b*d+a*i-c*g+e*i-f*h
    return (-determinant, principal_two, -(a+e+i), Fraction(1))


def polynomial_remainder(dividend, divisor):
    remainder = list(dividend)
    while remainder and remainder[-1] == 0:
        remainder.pop()
    while len(remainder) >= len(divisor):
        factor = remainder[-1]/divisor[-1]
        offset = len(remainder)-len(divisor)
        for index, coefficient in enumerate(divisor):
            remainder[offset+index] -= factor*coefficient
        while remainder and remainder[-1] == 0:
            remainder.pop()
    return tuple(remainder)


@dataclass(frozen=True)
class Form:
    label: str
    annihilator: tuple[Fraction, ...]
    values: tuple[Fraction, ...]


def bounded_forms():
    forms = []

    def add(label, annihilator, term):
        values = tuple(term(n) for n in range(8))
        need(all(0 <= value <= 1 for value in values), "unbounded form seed")
        forms.append(Form(label, annihilator, values))

    add("zero", (Fraction(1),), lambda _n: Fraction(0))
    add("one", (-Fraction(1), Fraction(1)), lambda _n: Fraction(1))
    add("x_power", (-X, Fraction(1)), lambda n: X**n)
    add("delta0", (Fraction(0), Fraction(1)), lambda n: Fraction(n == 0))
    alphabet = (Fraction(0), X, Fraction(1))
    for first in alphabet:
        for second in alphabet:
            add(f"finite:{first}:{second}", (0, 0, 1),
                lambda n, a=first, b=second: a if n == 0 else b if n == 1 else 0)
    for first in (Fraction(0), Fraction(1)):
        for tail in (X, Fraction(1)):
            add(f"flat_tail:{first}:{tail}", (0, -1, 1),
                lambda n, a=first, b=tail: a if n == 0 else b)
            add(f"x_tail:{first}:{tail}", (0, -X, 1),
                lambda n, a=first, b=tail: a if n == 0 else b*X**(n-1))
    for ratio in (Fraction(1), X, X**2):
        for even in alphabet:
            for odd in alphabet:
                add(f"parity:{ratio}:{even}:{odd}", (-ratio, 0, 1),
                    lambda n, r=ratio, a=even, b=odd:
                    (a if n % 2 == 0 else b)*r**(n//2))
    need(2*X < 1, "derivative sequence ratio")
    for scale in (X, Fraction(1)):
        add(f"derivative:{scale}", (X**2, -2*X, 1),
            lambda n, c=scale: 0 if n == 0 else c*n*X**(n-1))
    return tuple(forms)


def certify_all_lengths(delta, accepting):
    size = len(delta)
    actual = weighted_sequence(delta, accepting, size-1)
    charpoly = characteristic(weighted_matrix(delta))
    certificates = []
    for form in bounded_forms():
        if (form.values[:size] == actual
                and not polynomial_remainder(charpoly, form.annihilator)):
            certificates.append(form)
    need(certificates, "missing all-length sequence certificate")
    chosen = min(certificates, key=lambda form: (len(form.annihilator), form.label))
    # Cayley-Hamilton plus the first `size` terms proves equality for all n.
    need(all(0 <= value <= 1 for value in chosen.values), "certificate bound")
    return chosen.label


def enumerate_complete_dfas(states):
    for flat in product(range(states), repeat=2*states):
        delta = tuple((flat[2*q], flat[2*q+1]) for q in range(states))
        for accepting_mask in range(1 << states):
            yield delta, accepting_mask


def verify_dfa_claims():
    accept_all = ((0, 0),)
    need(not globally_safe_counts(accept_all, 1), "accept-all planted unsafe")
    all_ones = ((1, 0), (1, 1))
    need(globally_safe_counts(all_ones, 1), "all-ones planted safe")
    exact_singleton = ((0, 1), (1, 2), (2, 2))
    need(not globally_safe_counts(exact_singleton, 1 << 1),
         "exact-singleton planted unsafe")

    for states in (1, 2):
        for delta, accepting_mask in enumerate_complete_dfas(states):
            need(globally_safe_counts(delta, accepting_mask)
                 == globally_safe_ordered(delta, accepting_mask),
                 "count quotient disagrees with ordered product")

    expected = {1: (2, 1, 1), 2: (64, 23, 4), 3: (5832, 1454, 27)}
    language_sets = {}
    for states in (1, 2, 3):
        total = safe = 0
        languages = set()
        for delta, accepting_mask in enumerate_complete_dfas(states):
            total += 1
            if not globally_safe_counts(delta, accepting_mask):
                continue
            safe += 1
            languages.add(canonical_minimal(delta, accepting_mask))
            # Independent finite-horizon consistency check; the all-length
            # proof below is on the distinct minimal languages.
            sequence = weighted_sequence(
                delta, tuple(q for q in range(states)
                             if accepting_mask >> q & 1), 96)
            need(all(value <= 1 for value in sequence),
                 "safe presentation exceeds mass one")
            need(all(value <= Y**d for d, value in enumerate(sequence)),
                 "safe presentation exceeds gate")
        need((total, safe, len(languages)) == expected[states],
             "complete DFA census")
        language_sets[states] = languages

    need(language_sets[1] <= language_sets[3]
         and language_sets[2] <= language_sets[3],
         "three-state padding failed")
    form_histogram = Counter()
    for delta, accepting in language_sets[3]:
        form_histogram[certify_all_lengths(delta, accepting)] += 1
    need(sum(form_histogram.values()) == 27, "all-length certificate census")
    return expected, form_histogram


def main():
    initial_hashes = source_snapshot()
    need(X == Fraction(40, 597), "x constant")
    need(Y == Fraction(2401, 2388), "y constant")
    multiset_histogram = verify_multiset_equivalence()
    print("PASS_INDEPENDENT_MULTISET_EQUIVALENCE",
          tuple(sorted(multiset_histogram.items())))
    verify_tensor_and_uniformization_algebra()
    print("PASS_INDEPENDENT_TENSOR_UNIFORMIZATION")
    verify_uniform_extrema_and_recursion()
    print("PASS_INDEPENDENT_M1_M2_2K7_RECURSION")
    seams = verify_exact_lym_lp()
    print("PASS_INDEPENDENT_LYM_PRIMAL_DUAL", seams)
    dfa_counts, form_histogram = verify_dfa_claims()
    print("PASS_INDEPENDENT_DFA_ALL_LENGTHS", dfa_counts,
          "forms", tuple(sorted(form_histogram.items())))
    need(source_snapshot() == initial_hashes, "source mutated during audit")
    print("SOURCE_PACKET_NONMUTATION_OK")
    print("APPROVE_WEIGHTED_MULTISET7_SUNFLOWER_PACKET")


if __name__ == "__main__":
    main()
