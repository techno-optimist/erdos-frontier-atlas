#!/usr/bin/env python3
"""Independent stdlib replay of the aligned r=4/q=24 microbox wall.

This script imports no producer/discovery module and uses no optimization
package.  It reconstructs the 117-cell alphabet, the complete q=24
microboxes, the lexicographically first componentwise maximum dilation
matching, and every surviving order-four translation orbit in the natural
two-coordinate fibers.  It then checks the physical midpoint semantics,
strict interiors, cancellation, disjointness, and exact EHPS gate.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json

Q = 6
R = 4
FINE_Q = Q * R

ANCHORS = (
    (3, 2), (3, 3), (3, 4),
    (4, 1), (4, 2), (4, 3),
    (5, 0), (5, 1), (5, 2),
)
SHIFTS = (
    (0, 4), (1, 4), (1, 5), (2, 1), (2, 3), (3, 5),
    (4, 0), (4, 4), (4, 5), (5, 0), (5, 1), (5, 2), (5, 3),
)

COARSE = tuple(
    (a, b, (a + s) % Q, (b + t) % Q)
    for a, b in ANCHORS for s, t in SHIFTS
)
SUBDIGITS = tuple(product(range(R), repeat=4))
LABELS = tuple(
    (cell, beta)
    for cell in range(len(COARSE)) for beta in SUBDIGITS
)
DIGITS = tuple(
    tuple(R * COARSE[cell][j] + beta[j] for j in range(4))
    for cell, beta in LABELS
)
INDEX = {label: i for i, label in enumerate(LABELS)}


class AuditError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def dilation_edges() -> tuple[tuple[tuple[int, tuple[int, ...]], tuple[int, tuple[int, ...]]], ...]:
    """Enumerate the claimed coarse-active dilation subgraph.

    Fine-grid adjacencies internal to one coarse q=6 cell are deliberately
    not included.  This is a valid subgraph: on each coarse-active coordinate
    the source is the low residual quarter and the target is the high quarter
    of its coarse predecessor; inactive coarse coordinates keep one residual
    quarter.  At least one active coordinate must be the genuine 0 -> 5 wrap.
    """
    by_digits = {d: LABELS[i] for i, d in enumerate(DIGITS)}
    edges = set()
    for i, source_digits in enumerate(DIGITS):
        for changed in product((0, 1), repeat=4):
            if not any(changed):
                continue
            target_digits = tuple(
                (source_digits[j] - changed[j]) % FINE_Q for j in range(4)
            )
            target = by_digits.get(target_digits)
            if target is None:
                continue
            source = LABELS[i]
            source_cell, source_sub = source
            target_cell, target_sub = target
            A, B = COARSE[source_cell], COARSE[target_cell]
            active = tuple(j for j in range(4) if A[j] != B[j])
            if not active:
                continue
            if not all(B[j] == A[j] or B[j] == (A[j] - 1) % Q
                       for j in range(4)):
                continue
            if not all(source_sub[j] == 0 and target_sub[j] == R - 1
                       for j in active):
                continue
            if not all(source_sub[j] == target_sub[j]
                       for j in range(4) if j not in active):
                continue
            if not any(A[j] == 0 and B[j] == Q - 1 for j in active):
                continue
            edge = tuple(sorted((source, target)))
            require(len(set(edge)) == 2, "dilation loop")
            edges.add(edge)
    return tuple(sorted(edges))


def components(edges):
    adjacency = defaultdict(set)
    for x, y in edges:
        adjacency[x].add(y)
        adjacency[y].add(x)
    unseen = set(adjacency)
    result = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        comp = {root}
        queue = deque((root,))
        while queue:
            x = queue.popleft()
            for y in sorted(adjacency[x]):
                if y in unseen:
                    unseen.remove(y)
                    comp.add(y)
                    queue.append(y)
        result.append(tuple(sorted(comp)))
    return tuple(sorted(result))


def component_maximum_matching(comp, all_edges):
    """Exhaustive solver-free maximum matching, lexicographic tie-break."""
    local = tuple(e for e in all_edges if e[0] in comp and e[1] in comp)
    for size in range(min(len(comp) // 2, len(local)), -1, -1):
        for chosen in combinations(local, size):
            flat = tuple(v for edge in chosen for v in edge)
            if len(flat) == len(set(flat)):
                return chosen
    raise AuditError("matching search failed")


def canonical_matching(edges):
    chosen = []
    for comp in components(edges):
        chosen.extend(component_maximum_matching(comp, edges))
    return tuple(sorted(chosen))


def validate_dilation(edge) -> tuple[int, int]:
    (source_cell, source_sub), (target_cell, target_sub) = edge
    # The sorted storage loses orientation; recover the unique predecessor
    # orientation and then check its coarse/subdigit description.
    candidates = (
        ((source_cell, source_sub), (target_cell, target_sub)),
        ((target_cell, target_sub), (source_cell, source_sub)),
    )
    oriented = []
    for source, target in candidates:
        sd = DIGITS[INDEX[source]]
        td = DIGITS[INDEX[target]]
        delta = tuple((sd[j] - td[j]) % FINE_Q for j in range(4))
        if all(x in (0, 1) for x in delta) and any(delta) and any(
            delta[j] == 1 and sd[j] == 0 for j in range(4)
        ):
            oriented.append((source, target))
    require(len(oriented) == 1, "dilation orientation not unique")
    source, target = oriented[0]
    sc, ss = source
    tc, ts = target
    A, B = COARSE[sc], COARSE[tc]
    active = tuple(j for j in range(4) if A[j] != B[j])
    wraps = tuple(j for j in active if A[j] == 0 and B[j] == Q - 1)
    require(active and wraps, "no genuine coarse wrap")
    require(all(B[j] == A[j] or B[j] == (A[j] - 1) % Q for j in range(4)),
            "bad coarse predecessor")
    require(all(ss[j] == 0 and ts[j] == R - 1 for j in active),
            "bad active residual endpoint")
    require(all(ss[j] == ts[j] for j in range(4) if j not in active),
            "inactive residual mismatch")
    return INDEX[source], INDEX[target]


def scalar_correction_cost(a: int, t: F) -> tuple[F, F]:
    b = (a - 1) % Q
    A_t = F(a, Q) + t / Q
    A_3t = F(a, Q) + 3 * t / Q
    B_t = F(b + 1, Q) - t / Q
    B_3t = F(b + 1, Q) - 3 * t / Q

    def row(x: F, y: F, z: F) -> F:
        carry = x + z - 2 * y
        require(carry.denominator == 1, "dilation row is not modular")
        return Q * Q * ((x - z) ** 2 - 2*x*x - 2*z*z + 4*y*y)

    return row(A_t, B_t, B_3t), row(A_3t, A_t, B_t)


def exact_dilation_rows(source: int, target: int, t: F) -> None:
    """Replay both actual four-dimensional strict-interior rows."""
    source_cell, source_sub = LABELS[source]
    target_cell, target_sub = LABELS[target]
    A, B = COARSE[source_cell], COARSE[target_cell]
    active = tuple(j for j in range(4) if A[j] != B[j])
    wraps = tuple(j for j in active if A[j] == 0 and B[j] == Q - 1)

    def X(scale: int):
        return tuple(
            F(A[j], Q) + scale*t/Q if j in active
            else F(A[j], Q) + F(2*source_sub[j] + 1, 2*R*Q)
            for j in range(4)
        )

    def Y(scale: int):
        return tuple(
            F(B[j] + 1, Q) - scale*t/Q if j in active
            else F(B[j], Q) + F(2*target_sub[j] + 1, 2*R*Q)
            for j in range(4)
        )

    rows = ((X(1), Y(1), Y(3), -1), (X(3), X(1), Y(1), 1))
    labels = ((source, target, target), (source, source, target))
    correction_costs = []
    for (x, y, z, wrap_sign), point_labels in zip(rows, labels):
        carry = tuple(x[j] + z[j] - 2*y[j] for j in range(4))
        require(all(value.denominator == 1 for value in carry),
                "physical dilation row is not modular")
        expected = tuple(wrap_sign if j in wraps else 0 for j in range(4))
        require(carry == expected, "physical dilation carry mismatch")
        raw = sum((x[j] - z[j])**2 for j in range(4))
        require(raw > 0, "physical dilation raw RHS is zero")
        for point, vertex in zip((x, y, z), point_labels):
            digits = DIGITS[vertex]
            require(all(F(digits[j], FINE_Q) < point[j] <
                        F(digits[j] + 1, FINE_Q) for j in range(4)),
                    "dilation point leaves strict microbox interior")
        correction_costs.append(Q*Q*sum(
            (x[j]-z[j])**2 - 2*x[j]**2 - 2*z[j]**2 + 4*y[j]**2
            for j in range(4)
        ))
    K = len(wraps)
    require(correction_costs[0] == K*(108 - 24*t),
            "first physical correction cost mismatch")
    require(correction_costs[1] == K*(-36 - 24*t),
            "second physical correction cost mismatch")
    require(sum(correction_costs) == K*(72 - 48*t) > 0,
            "physical dilation recurrence is not positive")


def validate_dilation_semantics(matching) -> set[int]:
    endpoints = []
    wrap_hist = Counter()
    for edge in matching:
        source, target = validate_dilation(edge)
        endpoints.extend((source, target))
        A = COARSE[LABELS[source][0]]
        B = COARSE[LABELS[target][0]]
        wrap_hist[sum(a == 0 and b == Q - 1 for a, b in zip(A, B))] += 1
        exact_dilation_rows(source, target, F(1, 24))
    require(len(matching) == 960, "wrong matching cardinality")
    require(len(endpoints) == len(set(endpoints)) == 1920,
            "dilation matching overlaps")
    require(all(k >= 1 for k in wrap_hist), "zero-wrap edge")

    for a in range(Q):
        for t in (F(1, 100), F(1, 9), F(1, 7)):
            first, second = scalar_correction_cost(a, t)
            if a == 0:
                require(first == 108 - 24*t, "first wrap identity")
                require(second == -36 - 24*t, "second wrap identity")
                require(first + second == 72 - 48*t > 0,
                        "dilation increment not positive")
            else:
                require(first == second == 0, "nonwrap correction")

    T = F(1, 2 * R)
    for j in range(1, 12):
        t = T / 3**j
        require(0 < t < 3*t <= T < F(1, R), "low quarter escape")
        require(F(R - 1, R) < 1 - 3*t < 1 - t < 1,
                "high quarter escape")
    # A bounded correction |H|<=M gives |D|<=2M.  The finite sum below
    # exceeds the possible |D(T)-D(T/3^N)|<=4M for a sufficiently large N.
    for M in (0, 1, 10**3, 10**9):
        N = int((4*M + 24*T) // 72) + 1
        coarse_lower = 72*N - 24*T
        require(coarse_lower > 4*M, "finite dilation telescope too weak")
        if N <= 100:
            exact_lower = 72*N - 24*T*(1 - F(1, 3**N))
            require(exact_lower > coarse_lower,
                    "exact telescope correction has wrong sign")
    return set(endpoints)


def fiber_key(vertex: int) -> tuple[int, int, int]:
    cell, beta = LABELS[vertex]
    return cell // len(SHIFTS), beta[0], beta[1]


def translation_packets(vertices: set[int]):
    """Complete orbits of the claimed fixed shift (6,12) in one fiber."""
    lookup = {DIGITS[v][2:]: v for v in vertices}
    shift = (6, 12)
    require(tuple((4*s) % FINE_Q for s in shift) == (0, 0),
            "fixed shift does not have order dividing four")
    require(tuple((2*s) % FINE_Q for s in shift) != (0, 0),
            "fixed shift does not have exact order four")
    packet_generator = {}
    for start_vertex in sorted(vertices):
        start = DIGITS[start_vertex][2:]
        codes = tuple(
            tuple((start[j] + k*shift[j]) % FINE_Q for j in range(2))
            for k in range(4)
        )
        orbit = tuple(lookup.get(code, -1) for code in codes)
        if -1 in orbit or len(set(orbit)) != 4:
            continue
        packet = tuple(sorted(orbit))
        packet_generator.setdefault(packet, shift)
    return tuple(sorted(packet_generator)), packet_generator


def validate_packet(packet, shift) -> tuple[int, Counter]:
    support = set(packet)
    require(len(packet) == len(support) == 4, "packet is not order four")
    lookup = {DIGITS[v][2:]: v for v in packet}
    incidence = Counter()
    rhs = 0
    carries = Counter()
    centers = []
    sample_u = (F(1, 11), F(2, 11), F(3, 11), F(4, 11))
    for y in packet:
        yc = DIGITS[y]
        xcode = tuple((yc[j+2] - shift[j]) % FINE_Q for j in range(2))
        zcode = tuple((yc[j+2] + shift[j]) % FINE_Q for j in range(2))
        x, z = lookup.get(xcode), lookup.get(zcode)
        require(x in support and z in support and x != z,
                "translation neighbours not distinct support vertices")
        defect = tuple(DIGITS[x][j] + DIGITS[z][j] - 2*yc[j]
                       for j in range(4))
        require(all(value % FINE_Q == 0 for value in defect),
                "non-modular packet row")
        carry = tuple(value // FINE_Q for value in defect)
        carries[carry] += 1
        raw = sum((DIGITS[x][j] - DIGITS[z][j])**2 for j in range(4))
        require(raw > 0, "packet row has zero raw RHS")
        incidence[x] += 1
        incidence[z] += 1
        incidence[y] -= 2
        rhs += raw
        centers.append(y)

        xp = tuple(F(DIGITS[x][j], FINE_Q) + sample_u[j]/FINE_Q for j in range(4))
        yp = tuple(F(DIGITS[y][j], FINE_Q) + sample_u[j]/FINE_Q for j in range(4))
        zp = tuple(F(DIGITS[z][j], FINE_Q) + sample_u[j]/FINE_Q for j in range(4))
        require(all(0 < sample_u[j] < 1 for j in range(4)), "noninterior offset")
        require(all(xp[j] + zp[j] - 2*yp[j] == carry[j] for j in range(4)),
                "physical midpoint/carry mismatch")
        require(sum((xp[j] - zp[j])**2 for j in range(4)) == F(raw, FINE_Q**2),
                "physical raw-canonical cost mismatch")
    require(tuple(sorted(centers)) == packet, "centres do not equal support")
    require(all(value == 0 for value in incidence.values()),
            "arbitrary-potential coefficients do not cancel")
    require(rhs > 0, "packet weighted RHS is not positive")
    return rhs, carries


def main() -> None:
    require(len(COARSE) == len(set(COARSE)) == 117, "coarse alphabet collision")
    require(len(LABELS) == len(set(LABELS)) == 29952, "label collision")
    require(len(DIGITS) == len(set(DIGITS)) == 29952, "physical digit collision")

    edges = dilation_edges()
    require(len(edges) == 1359, "wrong dilation edge census")
    comps = components(edges)
    require(max(map(len, comps)) == 9, "unexpected large matching component")
    matching = canonical_matching(edges)
    blocked = validate_dilation_semantics(matching)

    fibers = defaultdict(set)
    for vertex in range(len(LABELS)):
        if vertex not in blocked:
            fibers[fiber_key(vertex)].add(vertex)
    require(len(fibers) == 144, "wrong fiber count")

    packets = []
    generators = []
    candidate_hist = Counter()
    for key in sorted(fibers):
        local, local_generators = translation_packets(fibers[key])
        candidate_hist[len(local)] += 1
        used = set()
        for packet in local:
            require(used.isdisjoint(packet), f"overlapping candidates in fiber {key}")
            used.update(packet)
            packets.append((key, packet))
            generators.append(local_generators[packet])
    require(len(packets) == 833, "wrong translation packet count")
    require(all(len(packet) == 4 for _, packet in packets), "non-order-four packet")
    require(set(generators) == {(6, 12)}, "packets are not the claimed fixed-shift orbits")

    all_used = set(blocked)
    total_rhs = 0
    carry_hist = Counter()
    for (key, packet), shift in zip(packets, generators):
        require(all(fiber_key(v) == key for v in packet), "packet escapes fiber")
        require(all_used.isdisjoint(packet), "obstruction supports overlap")
        rhs, carries = validate_packet(packet, shift)
        total_rhs += rhs
        carry_hist.update(carries)
        all_used.update(packet)
    require(len(all_used) == 1920 + 4*833, "used-vertex total mismatch")

    total = 117 * R**4
    gate = F(49, 576) * FINE_Q**4
    obstructions = len(matching) + len(packets)
    require(total == 29952, "wrong total")
    require(gate == 28224, "wrong exact gate")
    require(obstructions == 1793 > 1728, "packing does not cross deletion threshold")
    require(total - obstructions == 28159 < gate, "retained count not below gate")
    require(total - 1727 == 28225 > gate, "strict-above-gate budget mismatch")

    matching_serial = tuple(
        tuple(tuple((cell, tuple(beta))) for cell, beta in edge)
        for edge in matching
    )
    packet_serial = tuple(
        (key, packet, shift)
        for (key, packet), shift in zip(packets, generators)
    )
    print("PASS_INDEPENDENT_R4_Q24_MICROBOX_WALL")
    print("GEOMETRY_OK coarse=117 q24_microboxes=29952 physical_codes_unique")
    print(f"DILATION_OK edges={len(edges)} matching={len(matching)} endpoints={len(blocked)} components={len(comps)}")
    print(f"PACKETS_OK count={len(packets)} rows={4*len(packets)} vertices={4*len(packets)} total_raw_numerator={total_rhs}")
    print(f"FIBERS_OK count={len(fibers)} candidate_count_hist={dict(sorted(candidate_hist.items()))}")
    print(f"CARRIES_OK distinct={len(carry_hist)} rows={sum(carry_hist.values())}")
    print(f"DISJOINT_OK obstructions={obstructions} used_vertices={len(all_used)}")
    print(f"GATE_OK total={total} allowed_deletions=1727 forced_deletions={obstructions} max_retained={total-obstructions} gate={gate}")
    print(f"MATCHING_DIGEST {digest(matching_serial)}")
    print(f"PACKET_DIGEST {digest(packet_serial)}")
    print("DEPENDENCIES_OK stdlib_only no_import no_solver")
    print("SCOPE complete_aligned_q24_microbox_unions_only pointwise_raw_canonical")


if __name__ == "__main__":
    main()
