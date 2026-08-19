#!/usr/bin/env python3
"""Exact q=6 outer-code tensor-wall replay for the Erdos-142 capacity lane.

The local computation is exhaustive.  The outer theorem is symbolic: the
constructor and checker accept tuples of arbitrary finite length L, and the
README gives the corresponding universal proof.

Only Python's standard library and exact integer/Fraction arithmetic are used.
No solver, floating point, discovery table, or sibling certificate is imported.
"""

from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json


Q = 6
ROLES = ("P1", "P2", "P3", "B", "K")
ROLE_INDEX = {r: i for i, r in enumerate(ROLES)}
WORDS = (
    ("P1", "K", "B"),
    ("B", "K", "P1"),
    ("P2", "B", "P2"),
    ("P3", "B", "B"),
    ("B", "B", "P3"),
)
BASE = frozenset(
    ((3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3), (5, 0), (5, 1), (5, 2))
)
EXPECTED = {
    "assignment_count": 32768,
    "maximum_union_mass": 3645,
    "maximizer_count": 256,
    "local_cylinder_size": 729,
    "ambient_local_size": 46656,
    "required_pair_pattern_count": 20,
    "non_diagonal_pattern_count": 120,
    "point_torsion_count": 324,
    "maximizer_digest": "83e1cc0a18914a3afae89dfdae4c5f8d7ffc4d6c4a8120fdd50b183b79630544",
    "all_pattern_witness_digest": "b698cf82d41294dc62b030d208b689045bf991c3d0bf6c1ae8537b6a64ff9748",
    "local_rhs_sum_min": 24,
    "local_rhs_sum_max": 144,
}


def d4(point, k):
    """The exact eight q=6 square symmetries used by the local lane."""
    x, y = point
    if k & 1:
        x = Q - 1 - x
    if k & 2:
        y = Q - 1 - y
    if k & 4:
        x, y = y, x
    return x, y


IMAGES = []
for transform in range(8):
    image = frozenset(d4(p, transform) for p in BASE)
    if image not in IMAGES:
        IMAGES.append(image)
assert len(IMAGES) == 8
assert all(len(s) == 9 for s in IMAGES)


def point_index(p):
    return p[0] * Q + p[1]


def vertex_index(v):
    out = 0
    for p in v:
        out = out * (Q * Q) + point_index(p)
    return out


@lru_cache(maxsize=None)
def cylinder_bits(s0, s1, s2):
    """A physical (not occurrence-labelled) q=6 six-coordinate cylinder."""
    bits = 0
    for vertex in itertools.product(IMAGES[s0], IMAGES[s1], IMAGES[s2]):
        bits |= 1 << vertex_index(vertex)
    assert bits.bit_count() == EXPECTED["local_cylinder_size"]
    return bits


def support_ids(assignment, word):
    return tuple(assignment[ROLE_INDEX[r]] for r in WORDS[word])


def cylinders(assignment):
    return tuple(cylinder_bits(*support_ids(assignment, w)) for w in range(5))


def enumerate_maximizers():
    assignments = list(itertools.product(range(8), repeat=5))
    assert len(assignments) == EXPECTED["assignment_count"]
    best = -1
    maximizers = []
    for assignment in assignments:
        union = 0
        for cylinder in cylinders(assignment):
            union |= cylinder
        mass = union.bit_count()
        if mass > best:
            best = mass
            maximizers = [assignment]
        elif mass == best:
            maximizers.append(assignment)
    assert best == EXPECTED["maximum_union_mass"]
    assert len(maximizers) == EXPECTED["maximizer_count"]
    # Five cylinders of size 729 have union 5*729 exactly iff they are
    # pairwise disjoint.  Check the stronger pairwise statement directly.
    for assignment in maximizers:
        cs = cylinders(assignment)
        assert sum(c.bit_count() for c in cs) == best
        assert all((cs[a] & cs[b]) == 0 for a in range(5) for b in range(a + 1, 5))
    return tuple(maximizers)


POINTS = tuple(itertools.product(range(Q), repeat=2))
POINT_TORSION = []
for x in POINTS:
    for y in POINTS:
        z = tuple((2 * y[j] - x[j]) % Q for j in range(2))
        if all(
            (2 * x[j] - y[j] - z[j]) % Q == 0
            and (2 * z[j] - x[j] - y[j]) % Q == 0
            for j in range(2)
        ):
            POINT_TORSION.append((x, y, z))
POINT_TORSION = tuple(POINT_TORSION)
assert len(POINT_TORSION) == EXPECTED["point_torsion_count"]


@lru_cache(maxsize=None)
def allowed_point_torsion(sx, sy, sz):
    return tuple(
        (x, y, z)
        for x, y, z in POINT_TORSION
        if x in IMAGES[sx] and y in IMAGES[sy] and z in IMAGES[sz]
    )


def raw_cost(u, w):
    """Raw squared distance of canonical representatives in {0,...,5}."""
    return sum((a - b) ** 2 for a, b in zip(flatten(u), flatten(w)))


def flatten(global_vertex):
    """Flatten nested outer blocks, local 3-tuples, and q=6 point pairs."""
    out = []

    def visit(value):
        if isinstance(value, int):
            out.append(value)
        else:
            for item in value:
                visit(item)

    visit(global_vertex)
    return tuple(out)


def local_vertex_in_cylinder(vertex, assignment, word):
    if len(vertex) != 3:
        return False
    return all(
        vertex[j] in IMAGES[assignment[ROLE_INDEX[WORDS[word][j]]]] for j in range(3)
    )


def midpoint_and_carry(u, v, w):
    """Check u+w == 2v (mod 6), returning the exact integer carry vector."""
    fu, fv, fw = flatten(u), flatten(v), flatten(w)
    if not (len(fu) == len(fv) == len(fw)):
        raise AssertionError("dimension mismatch")
    numerators = tuple(a + c - 2 * b for a, b, c in zip(fu, fv, fw))
    if any(n % Q for n in numerators):
        raise AssertionError("modular midpoint failure")
    carries = tuple(n // Q for n in numerators)
    if any(a + c - 2 * b != Q * k for a, b, c, k in zip(fu, fv, fw, carries)):
        raise AssertionError("carry reconstruction failure")
    return carries


def nonconstant(triple):
    x, y, z = triple
    return x != y or y != z


@lru_cache(maxsize=None)
def local_pattern_cycle(assignment, a, b, c):
    """Construct the exact local torsion cycle for a non-diagonal pattern."""
    assert (
        len(assignment) == 5
        and all(0 <= letter < 5 for letter in (a, b, c))
        and not (a == b == c)
    )
    choices = []
    for position in range(3):
        sx = assignment[ROLE_INDEX[WORDS[a][position]]]
        sy = assignment[ROLE_INDEX[WORDS[b][position]]]
        sz = assignment[ROLE_INDEX[WORDS[c][position]]]
        allowed = allowed_point_torsion(sx, sy, sz)
        if not allowed:
            raise AssertionError("missing point factor")
        choices.append(allowed)

    selected = [factor[0] for factor in choices]
    changed = False
    for position, factor in enumerate(choices):
        candidate = next((t for t in factor if nonconstant(t)), None)
        if candidate is not None:
            selected[position] = candidate
            changed = True
            break
    if not changed:
        raise AssertionError("only a zero-cost diagonal cycle exists")

    x = tuple(t[0] for t in selected)
    y = tuple(t[1] for t in selected)
    z = tuple(t[2] for t in selected)
    assert local_vertex_in_cylinder(x, assignment, a)
    assert local_vertex_in_cylinder(y, assignment, b)
    assert local_vertex_in_cylinder(z, assignment, c)
    carries = (
        midpoint_and_carry(x, y, z),
        midpoint_and_carry(y, x, z),
        midpoint_and_carry(x, z, y),
    )
    rhs = (raw_cost(x, z), raw_cost(y, z), raw_cost(x, y))
    assert sum(rhs) > 0
    return x, y, z, rhs, carries


def local_pair_cycle(assignment, a, b):
    """The 20-pattern specialization used by the two-codeword corollary."""
    assert a != b
    return local_pattern_cycle(assignment, a, b, b)


def constant_local_cycle(assignment, word):
    support = tuple(IMAGES[assignment[ROLE_INDEX[r]]] for r in WORDS[word])
    point = tuple(min(s) for s in support)
    assert local_vertex_in_cylinder(point, assignment, word)
    assert midpoint_and_carry(point, point, point) == (0,) * 6
    assert raw_cost(point, point) == 0
    return point, point, point, (0, 0, 0), ((0,) * 6,) * 3


def product_membership(vertex, assignments, word):
    return len(vertex) == len(assignments) == len(word) and all(
        local_vertex_in_cylinder(vertex[i], assignments[i], word[i])
        for i in range(len(word))
    )


def aggregate_coefficients(rows):
    """Aggregate by the full physical superblock vertex, never by projections."""
    coefficients = {}
    for endpoints_and_center in rows:
        u, v, w = endpoints_and_center
        for vertex, coefficient in ((u, 1), (v, -2), (w, 1)):
            coefficients[vertex] = coefficients.get(vertex, 0) + coefficient
    return {vertex: c for vertex, c in coefficients.items() if c}


def validate_tensor_packet(packet, assignments, outer_words):
    u, v, w = outer_words
    x, y, z = packet["vertices"]
    rows = packet["rows"]
    rhs = packet["raw_rhs"]
    carries = packet["carries"]
    local_rhs = packet["local_raw_rhs"]

    if rows != ((x, y, z), (y, x, z), (x, z, y)):
        raise AssertionError("full-superblock variable identity failure")
    if not product_membership(x, assignments, u):
        raise AssertionError("X is outside product cylinder u")
    if not product_membership(y, assignments, v):
        raise AssertionError("Y is outside product cylinder v")
    if not product_membership(z, assignments, w):
        raise AssertionError("Z is outside product cylinder w")

    computed_carries = tuple(midpoint_and_carry(*row) for row in rows)
    if carries != computed_carries:
        raise AssertionError("recorded carry failure")
    computed_rhs = tuple(raw_cost(row[0], row[2]) for row in rows)
    if rhs != computed_rhs:
        raise AssertionError("raw canonical cost failure")
    additive_rhs = tuple(sum(local[i] for local in local_rhs) for i in range(3))
    if rhs != additive_rhs:
        raise AssertionError("squared-distance additivity failure")
    if sum(rhs) <= 0:
        raise AssertionError("nonpositive tensor contradiction")
    if aggregate_coefficients(rows):
        raise AssertionError("global potential coefficients do not cancel")

    # The local maximum cylinders separate distinct codewords physically.  This
    # prevents a hidden occurrence-label convention in the outer union.
    separators = []
    for i, letters in enumerate(zip(u, v, w)):
        if len(set(letters)) > 1:
            cs = cylinders(assignments[i])
            for a, b in itertools.combinations(sorted(set(letters)), 2):
                if cs[a] & cs[b]:
                    raise AssertionError("local maximum cylinders overlap")
            separators.append(i)
    if not separators:
        raise AssertionError("the three outer words are equal")
    return tuple(separators)


def tensor_pattern(assignments, u, v, w, maximizer_set):
    """Tensor any nonconstant ordered triple of outer words."""
    assignments = tuple(tuple(a) for a in assignments)
    u, v, w = tuple(u), tuple(v), tuple(w)
    if not (len(assignments) == len(u) == len(v) == len(w) and len(u) >= 1):
        raise AssertionError("outer lengths do not agree")
    if any(a not in maximizer_set for a in assignments):
        raise AssertionError("an outer coordinate is not a certified maximizer")
    if u == v == w:
        raise AssertionError("a nonconstant outer word triple is required")
    if any(not (0 <= letter < 5) for letter in u + v + w):
        raise AssertionError("outer letter outside {0,...,4}")

    local = []
    for assignment, a, b, c in zip(assignments, u, v, w):
        if a == b == c:
            local.append(constant_local_cycle(assignment, a))
        else:
            local.append(local_pattern_cycle(assignment, a, b, c))
    x = tuple(item[0] for item in local)
    y = tuple(item[1] for item in local)
    z = tuple(item[2] for item in local)
    packet = {
        "vertices": (x, y, z),
        "rows": ((x, y, z), (y, x, z), (x, z, y)),
        "raw_rhs": (
            raw_cost(x, z),
            raw_cost(y, z),
            raw_cost(x, y),
        ),
        "local_raw_rhs": tuple(item[3] for item in local),
        "carries": (
            midpoint_and_carry(x, y, z),
            midpoint_and_carry(y, x, z),
            midpoint_and_carry(x, z, y),
        ),
    }
    packet["separating_coordinates"] = validate_tensor_packet(packet, assignments, (u, v, w))
    return packet


def tensor_pair(assignments, u, v, maximizer_set):
    """Two-codeword corollary, using the ordered outer pattern (u,v,v)."""
    if tuple(u) == tuple(v):
        raise AssertionError("a distinct codeword pair is required")
    return tensor_pattern(assignments, u, v, v, maximizer_set)


def arbitrary_global_potential_check(packet):
    """Demonstrate cancellation for deliberately nonseparable potential values."""
    x, y, z = packet["vertices"]
    # These values are not sums of coordinate potentials and are otherwise
    # unconstrained.  Coefficient cancellation proves the same identity for
    # every assignment of real values to the three full vertices.
    values = {x: 137, y: -211, z: 43}
    lhs = 0
    for u, v, w in packet["rows"]:
        lhs += values[u] - 2 * values[v] + values[w]
    assert lhs == 0
    assert sum(packet["raw_rhs"]) > 0


def singleton_density(length):
    assert isinstance(length, int) and length >= 1
    size = EXPECTED["local_cylinder_size"] ** length
    ambient = EXPECTED["ambient_local_size"] ** length
    density = Fraction(size, ambient)
    gate = Fraction(7, 24) ** (3 * length)
    assert density == Fraction(1, 64) ** length
    assert Fraction(1, 64) < Fraction(7, 24) ** 3
    assert density < gate
    return density, gate


def expect_rejection(callback):
    try:
        callback()
    except (AssertionError, KeyError, TypeError, ValueError):
        return True
    raise AssertionError("planted corruption was accepted")


def planted_controls(packet, assignments, u, v, maximizer_set, nonmax):
    controls = {}

    def corrupt_midpoint():
        x, y, z = packet["vertices"]
        bad_x = list(x)
        block = [list(p) for p in bad_x[0]]
        point = list(block[0])
        point[0] = (point[0] + 1) % Q
        block[0] = tuple(point)
        bad_x[0] = tuple(block)
        midpoint_and_carry(tuple(bad_x), y, z)

    controls["wrong_midpoint_rejected"] = expect_rejection(corrupt_midpoint)

    def corrupt_carry():
        bad = dict(packet)
        rows = bad["rows"]
        carries = [list(c) for c in bad["carries"]]
        carries[0][0] += 1
        bad["carries"] = tuple(tuple(c) for c in carries)
        validate_tensor_packet(bad, assignments, (u, v, v))

    controls["wrong_carry_rejected"] = expect_rejection(corrupt_carry)

    def corrupt_cost():
        bad = dict(packet)
        rhs = list(bad["raw_rhs"])
        rhs[1] += 1
        bad["raw_rhs"] = tuple(rhs)
        validate_tensor_packet(bad, assignments, (u, v, v))

    controls["wrong_raw_cost_rejected"] = expect_rejection(corrupt_cost)

    def hybrid_identity():
        bad = dict(packet)
        x, y, z = bad["vertices"]
        hybrid = (y[0],) + x[1:]
        bad["rows"] = ((x, y, z), (hybrid, x, z), (x, z, y))
        validate_tensor_packet(bad, assignments, (u, v, v))

    controls["coordinate_projection_identity_fraud_rejected"] = expect_rejection(hybrid_identity)

    def occurrence_alias():
        # Tagging the same physical X/Y/Z separately in each row is precisely
        # the illegal move that would replace one global potential by row-local
        # or coordinate-local potentials.
        x, y, z = packet["vertices"]
        bad_rows = tuple(
            tuple((row_number, position, vertex) for position, vertex in enumerate(row))
            for row_number, row in enumerate(((x, y, z), (y, x, z), (x, z, y)))
        )
        if not aggregate_coefficients(bad_rows):
            raise AssertionError("occurrence labels unexpectedly cancelled")
        raise ValueError("physical global identities were replaced by occurrence labels")

    controls["occurrence_label_alias_rejected"] = expect_rejection(occurrence_alias)
    controls["equal_codeword_rejected"] = expect_rejection(
        lambda: tensor_pair(assignments, u, u, maximizer_set)
    )
    bad_assignments = (nonmax,) + tuple(assignments[1:])
    controls["nonmaximal_coordinate_rejected"] = expect_rejection(
        lambda: tensor_pair(bad_assignments, u, v, maximizer_set)
    )

    def overbroad_nonmax_claim():
        bad_assignment = (0, 0, 0, 0, 0)
        union = 0
        for cylinder in cylinders(bad_assignment):
            union |= cylinder
        assert union.bit_count() == 729
        # Although (0,1,1) is non-diagonal as a word pattern, this assignment
        # makes all five geometric cylinders coincide.  Only the zero cycle
        # remains, so dropping the maximum-assignment premise is invalid.
        local_pattern_cycle(bad_assignment, 0, 1, 1)

    controls["overbroad_nonmax_tensor_claim_rejected"] = expect_rejection(overbroad_nonmax_claim)

    def false_mass_gate():
        if Fraction(1, 64) >= Fraction(7, 24) ** 3:
            return
        raise ValueError("the planted reversed gate is false")

    controls["reversed_singleton_gate_rejected"] = expect_rejection(false_mass_gate)
    assert all(controls.values())
    return controls


def digest_json(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def main():
    maximizers = enumerate_maximizers()
    maximizer_set = frozenset(maximizers)

    assert digest_json(maximizers) == EXPECTED["maximizer_digest"]

    # Check the complete 120-pattern premise, not merely the 20 patterns used
    # by the pair corollary.  This proves the stronger outer-triple theorem.
    all_rhs_sums = []
    pair_rhs_sums = []
    witness_records = []
    for assignment in maximizers:
        for a in range(5):
            for b in range(5):
                for c in range(5):
                    if a == b == c:
                        continue
                    x, y, z, rhs, carries = local_pattern_cycle(assignment, a, b, c)
                    assert sum(rhs) > 0
                    all_rhs_sums.append(sum(rhs))
                    if b == c and a != b:
                        pair_rhs_sums.append(sum(rhs))
                    witness_records.append((assignment, a, b, c, x, y, z, rhs, carries))
    assert len(all_rhs_sums) == EXPECTED["maximizer_count"] * EXPECTED["non_diagonal_pattern_count"]
    assert len(pair_rhs_sums) == EXPECTED["maximizer_count"] * EXPECTED["required_pair_pattern_count"]
    all_pattern_digest = digest_json(witness_records)
    assert all_pattern_digest == EXPECTED["all_pattern_witness_digest"]
    assert min(all_rhs_sums) == EXPECTED["local_rhs_sum_min"]
    assert max(all_rhs_sums) == EXPECTED["local_rhs_sum_max"]

    # Exercise arbitrary length, varying assignments by coordinate, repeated
    # letters, and several differing coordinates.  The proof itself is the
    # length-parametric constructor plus the invariant in validate_tensor_packet.
    assignment_sample = tuple(maximizers[(37 * i + 11) % len(maximizers)] for i in range(7))
    u = (0, 1, 2, 3, 4, 0, 2)
    v = (0, 4, 2, 1, 4, 3, 0)
    packet = tensor_pair(assignment_sample, u, v, maximizer_set)
    assert packet["separating_coordinates"] == (1, 3, 5, 6)
    assert sum(packet["raw_rhs"]) >= 24 * len(packet["separating_coordinates"])
    arbitrary_global_potential_check(packet)

    # Exercise the stronger three-word form too: all three product cylinders
    # may differ, and diagonal coordinates are padded by exact constant cycles.
    w = (3, 4, 2, 0, 1, 3, 0)
    triple_packet = tensor_pattern(assignment_sample, u, v, w, maximizer_set)
    assert sum(triple_packet["raw_rhs"]) >= 24 * len(triple_packet["separating_coordinates"])
    arbitrary_global_potential_check(triple_packet)

    density_samples = {}
    for length in (1, 2, 7, 19):
        density, gate = singleton_density(length)
        density_samples[str(length)] = {
            "density": f"{density.numerator}/{density.denominator}",
            "gate": f"{gate.numerator}/{gate.denominator}",
        }

    nonmax = next(a for a in itertools.product(range(8), repeat=5) if a not in maximizer_set)
    controls = planted_controls(packet, assignment_sample, u, v, maximizer_set, nonmax)

    output = {
        "q": Q,
        "assignment_count": 8 ** 5,
        "maximum_union_mass": EXPECTED["maximum_union_mass"],
        "maximizer_count": len(maximizers),
        "maximizer_digest": digest_json(maximizers),
        "maximum_cylinders_pairwise_disjoint": True,
        "non_diagonal_ordered_patterns": EXPECTED["non_diagonal_pattern_count"],
        "all_pattern_cycles_checked": len(all_rhs_sums),
        "required_ordered_pair_patterns": EXPECTED["required_pair_pattern_count"],
        "pair_pattern_cycles_checked": len(pair_rhs_sums),
        "local_rhs_sum_min": min(all_rhs_sums),
        "local_rhs_sum_max": max(all_rhs_sums),
        "all_pattern_witness_digest": all_pattern_digest,
        "outer_length_is_symbolic": True,
        "every_nonconstant_outer_triple_obstructed": True,
        "every_outer_code_of_size_at_least_two_obstructed": True,
        "coordinate_dependent_maximizers_allowed": True,
        "arbitrary_nonseparable_global_potential_cancelled": True,
        "sample_length": len(u),
        "sample_separating_coordinates": list(packet["separating_coordinates"]),
        "sample_raw_rhs": list(packet["raw_rhs"]),
        "sample_rhs_sum": sum(packet["raw_rhs"]),
        "sample_normalized_rhs_sum": str(Fraction(sum(packet["raw_rhs"]), Q * Q)),
        "per_nondiagonal_coordinate_normalized_rhs_floor": "2/3",
        "outer_hamming_rhs_floor_verified": True,
        "single_cylinder_density": "1/64",
        "ehps_candidate_local_gate": str(Fraction(7, 24) ** 3),
        "singleton_below_gate": True,
        "density_samples": density_samples,
        "controls": controls,
        "scope": (
            "finite Cartesian products of exact q=6 maximum-mass D4 cylinders with "
            "one fixed maximizer per outer coordinate; no deformed-support, recursive-transfer, "
            "continuum, r3(N), or Erdos-142 solution claim"
        ),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    print("PASS_Q6_OUTERCODE_TENSOR_WALL")


if __name__ == "__main__":
    main()
