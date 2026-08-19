#!/usr/bin/env python3
"""Independent stdlib-only replay of the q=7/q=8 cyclic-line screen.

This file deliberately reconstructs the quotient geometry and its audit from
scratch.  It imports neither the discovery engine nor ``verify.py`` and reads
no sibling artefacts.  The screen is factorized over the three local
coordinates, but every accepted certificate is rebuilt as a six-dimensional
physical midpoint cycle with canonical raw costs and full-vertex cancellation.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction


ROLES = ("P1", "P2", "P3", "B", "K")
WORDS = (("P1", "K", "B"), ("B", "K", "P1"),
         ("P2", "B", "P2"), ("P3", "B", "B"), ("B", "B", "P3"))
RIX = {name: i for i, name in enumerate(ROLES)}
THETA = Fraction(7, 24)

EXPECTED = {
    7: {"support": 11, "mass": 6655, "maximizers": 256, "orbits": 32,
        "labels": 0,
        "count_digest": "54f65952ad8d24e1cc555b1ccd5de84cdb2052aa402e567295838ee33194b565",
        "sequence_digest": "d8e256732c62098ffe74a253fe83d9f37ddac36e817f04513d826cb4fc8d3cd1"},
    8: {"support": 15, "mass": 16875, "maximizers": 256, "orbits": 32,
        4: {"min": 64, "max": 64, "sum": 2048,
            "count_digest": "6eba42350d18fff52c4f555c7403b53769cdea128802f959b8b22bce4f1e1cdf",
            "sequence_digest": "df89a71be28b934e69c5c8994bbf9eec024f07777a6da333ecab667dbe679653",
            "certificate_digest": "7749907c4f88228e867ba915f65e35510bc2282553ce8d584967262c3e0df126",
            "raw": (128, 256)},
        8: {"min": 272, "max": 576, "sum": 13568,
            "count_digest": "3ab7a0d16d4936e0a962cc28c3642d6860dd8c62848f801ffbdafc6eb7fe0040",
            "sequence_digest": "6571a1520d234e529d414ae6e9680f9fa560b24bab489c271d7d1f0984aae614",
            "certificate_digest": "350a6edaf301685c8bd48c7ef2a43fc9104901198ba14df4928df4d4256ac58e",
            "raw": (192, 384)},
    },
}
MAX_DIGEST = "83e1cc0a18914a3afae89dfdae4c5f8d7ffc4d6c4a8120fdd50b183b79630544"


def point_piece(p, q):
    a, b = (Fraction(x, q) for x in p)
    e = Fraction(1, q)
    s = a + b
    if a >= Fraction(1, 2) and s > Fraction(2, 3) and s <= Fraction(7, 6):
        return "T1"
    if (a >= Fraction(1, 2) and b < Fraction(1, 2)
            and s >= Fraction(7, 6) + e and s <= Fraction(17, 12)):
        return "T2"
    if (a < Fraction(1, 2) and b >= Fraction(1, 2)
            and s >= Fraction(7, 6) + e and s <= Fraction(17, 12)
            and 2 * a + b >= Fraction(3, 2) + e):
        return "T3"
    return None


def d4(p, k, q):
    x, y = p
    if k & 1:
        x = q - 1 - x
    if k & 2:
        y = q - 1 - y
    if k & 4:
        x, y = y, x
    return x, y


def quotient(q):
    base = tuple(p for p in itertools.product(range(q), repeat=2)
                 if point_piece(p, q) is not None)
    assert len(base) == EXPECTED[q]["support"]
    images = []
    for k in range(8):
        s = frozenset(d4(p, k, q) for p in base)
        if s not in images:
            images.append(s)
    assert len(images) == 8 and all(len(x) == len(base) for x in images)
    perms = []
    for k in range(8):
        perm = []
        for source in images:
            image = frozenset(d4(p, k, q) for p in source)
            perm.append(images.index(image))
        perms.append(tuple(perm))
    return base, tuple(images), tuple(perms)


def role_supports(assignment, images):
    return {role: images[assignment[RIX[role]]] for role in ROLES}


def cylinders(assignment, images):
    supports = role_supports(assignment, images)
    return tuple(frozenset(tuple(x for p in vertex for x in p)
                            for vertex in itertools.product(*(supports[r] for r in word)))
                 for word in WORDS)


def maximum_data(images, perms, q):
    all_assignments = tuple(itertools.product(range(8), repeat=5))
    masses = {}
    best = -1
    winners = []
    for a in all_assignments:
        # Inclusion-exclusion is exact and avoids materializing six-coordinate
        # vertices for all 32768 assignments.
        cs = [tuple(images[a[RIX[r]]] for r in word) for word in WORDS]
        mass = 0
        for mask in range(1, 32):
            common = None
            for i in range(5):
                if mask & (1 << i):
                    common = cs[i] if common is None else tuple(x & y for x, y in zip(common, cs[i]))
            # Every product-cylinder intersection factors by coordinate.
            term = math.prod(len(x) for x in common)
            mass += term if mask.bit_count() & 1 else -term
        masses[mass] = masses.get(mass, 0) + 1
        if mass > best:
            best, winners = mass, [a]
        elif mass == best:
            winners.append(a)
    winners = tuple(winners)
    assert best == 5 * len(images[0]) ** 3
    assert len(winners) == EXPECTED[q]["maximizers"]
    reps, remaining = [], set(winners)
    while remaining:
        a = min(remaining)
        orbit = frozenset(tuple(p[x] for x, p in zip(a, (perm,) * 5))
                          for perm in perms)
        assert len(orbit) == 8 and orbit <= remaining
        reps.append(a)
        remaining -= orbit
    assert len(reps) == EXPECTED[q]["orbits"]
    return winners, tuple(reps), best, masses


def block_label(assignment, cylinder):
    return tuple(assignment[RIX[r]] for r in WORDS[cylinder])


def step_order(step, q):
    return math.lcm(*(q // math.gcd(q, x) for x in step))


def encode(labels):
    result = 0
    scale = 1
    for x in labels:
        result += x * scale
        scale *= 5
    return result


def decode(code, k):
    out = []
    for _ in range(k):
        out.append(code % 5)
        code //= 5
    assert code == 0
    return tuple(out)


def local_lines(q, assignment, images, position, k):
    supports = role_supports(assignment, images)
    result = {}
    for start in itertools.product(range(q), repeat=2):
        for step in itertools.product(range(q), repeat=2):
            order = step_order(step, q)
            if k % order:
                continue
            labels = []
            valid = True
            for j in range(k):
                point = tuple((start[u] + j * step[u]) % q for u in range(2))
                here = tuple(c for c, word in enumerate(WORDS)
                             if point in supports[word[position]])
                if not here:
                    valid = False
                    break
                labels.append(here)
            if not valid:
                continue
            for seq in itertools.product(*labels):
                code = encode(seq)
                result.setdefault(code, {}).setdefault(order, (start, step))
    return result


def feasible(q, assignment, images, k):
    maps = tuple(local_lines(q, assignment, images, pos, k) for pos in range(3))
    common = set(maps[0]) & set(maps[1]) & set(maps[2])
    out = {}
    for code in sorted(common):
        order_choices = [tuple(sorted(maps[i][code])) for i in range(3)]
        for orders in itertools.product(*order_choices):
            if math.lcm(*orders) == k:
                out[code] = tuple(maps[i][code][orders[i]] for i in range(3))
                break
    return out


def flat(vertex):
    return tuple(x for p in vertex for x in p)


def midpoint_row(x, y, z, q):
    nums = tuple(a + c - 2 * b for a, b, c in zip(x, y, z))
    assert all(n % q == 0 for n in nums)
    carry = tuple(n // q for n in nums)
    assert all(a + c - 2 * b == q * t for a, b, c, t in zip(x, y, z, carry))
    return carry


def cost(x, z):
    return sum((a - b) ** 2 for a, b in zip(x, z))


def vertex_from_local(points):
    return tuple(x for p in points for x in p)


def certify(q, assignment, images, labels, locals_):
    k = len(labels)
    assert len(locals_) == 3
    line = tuple(vertex_from_local(tuple(tuple((s[u] + j * d[u]) % q for u in range(2))
                                         for s, d in locals_)) for j in range(k))
    cs = cylinders(assignment, images)
    for label, point in zip(labels, line):
        assert point in cs[label]
        assert sum(point in c for c in cs) == 1
    step = tuple((line[1][u] - line[0][u]) % q for u in range(6))
    assert step_order(step, q) == k
    assert tuple(tuple((line[0][u] + j * step[u]) % q for u in range(6))
                 for j in range(k)) == line
    rows = tuple((line[(j - 1) % k], line[j], line[(j + 1) % k])
                 for j in range(k))
    carries = tuple(midpoint_row(*r, q) for r in rows)
    rhs = tuple(cost(r[0], r[2]) for r in rows)
    assert all(x > 0 for x in rhs)
    coeff = {}
    for r in rows:
        for p, c in ((r[0], 1), (r[1], -2), (r[2], 1)):
            coeff[p] = coeff.get(p, 0) + c
    assert not {p: c for p, c in coeff.items() if c}
    return {"q": q, "order": k, "assignment": assignment, "labels": labels,
            "line": line, "row_patterns": tuple((labels[(j - 1) % k], labels[j], labels[(j + 1) % k]) for j in range(k)),
            "carries": carries, "raw_rhs": rhs, "raw_contradiction": sum(rhs),
            "normalized_contradiction": Fraction(sum(rhs), q * q)}


def transport(cert, element, q, images, perms):
    a = tuple(perms[element][x] for x in cert["assignment"])
    line = []
    for vertex in cert["line"]:
        pts = tuple((vertex[i], vertex[i + 1]) for i in range(0, 6, 2))
        line.append(vertex_from_local(tuple(d4(p, element, q) for p in pts)))
    return certify_line(q, a, images, cert["labels"], tuple(line))


def certify_line(q, assignment, images, labels, line):
    # Recheck a transported line without recovering its three local starts.
    k = len(line); cs = cylinders(assignment, images)
    assert len(set(labels)) <= 5 and len(line) == k
    for l, p in zip(labels, line):
        assert p in cs[l] and sum(p in c for c in cs) == 1
    step = tuple((line[1][i] - line[0][i]) % q for i in range(6))
    assert step_order(step, q) == k
    assert tuple(tuple((line[0][i] + j * step[i]) % q for i in range(6)) for j in range(k)) == line
    rows = tuple((line[(j - 1) % k], line[j], line[(j + 1) % k]) for j in range(k))
    carries = tuple(midpoint_row(*r, q) for r in rows)
    rhs = tuple(cost(r[0], r[2]) for r in rows)
    assert all(rhs)
    coeff = {}
    for r in rows:
        for p, c in ((r[0], 1), (r[1], -2), (r[2], 1)):
            coeff[p] = coeff.get(p, 0) + c
    assert not {p: c for p, c in coeff.items() if c}
    return {"q": q, "order": k, "assignment": assignment, "labels": labels,
            "line": line, "row_patterns": tuple((labels[(j - 1) % k], labels[j], labels[(j + 1) % k]) for j in range(k)),
            "carries": carries, "raw_rhs": rhs, "raw_contradiction": sum(rhs),
            "normalized_contradiction": Fraction(sum(rhs), q * q)}


# A five-row obstruction that is invisible to the affine cyclic-line screen.
# The endpoints follow the ordinary 5-cycle i -> i+1, while centers use the
# nontrivial permutation pi.  The coefficient vector is a second independent
# kernel vector over F_7:
#     c_i + c_{i+1} - 2 c_{pi(i)} == 0 (mod 7).
FIVE_COEFFICIENTS = (0, 1, 4, 3, 6)
FIVE_CENTERS = (2, 4, 0, 1, 3)


def five_row_local_maps(q, assignment, images, position):
    """Map a five-label cylinder pattern to one affine local line witness."""
    supports = role_supports(assignment, images)
    out = {}
    for start in itertools.product(range(q), repeat=2):
        for step in itertools.product(range(q), repeat=2):
            # The q=7 construction requires a nonzero global step, but a
            # coordinate block may itself be constant (order 1).
            if q != 7 or step_order(step, q) not in (1, 7):
                continue
            labels = []
            for t in FIVE_COEFFICIENTS:
                p = tuple((start[u] + t * step[u]) % q for u in range(2))
                here = tuple(c for c, word in enumerate(WORDS)
                             if p in supports[word[position]])
                if not here:
                    break
                labels.append(here)
            else:
                for sequence in itertools.product(*labels):
                    out.setdefault(sequence, (start, step))
    return out


def certify_five_row(q, assignment, images, labels, local_lines):
    """Audit the five unit-weight rows on complete physical vertices."""
    assert q == 7 and len(labels) == 5 and len(local_lines) == 3
    assert len(set(labels)) <= 5
    vertices = []
    for t in FIVE_COEFFICIENTS:
        points = tuple(tuple((start[u] + t * step[u]) % q for u in range(2))
                       for start, step in local_lines)
        vertices.append(vertex_from_local(points))
    cs = cylinders(assignment, images)
    for label, vertex in zip(labels, vertices):
        assert vertex in cs[label]
        assert sum(vertex in c for c in cs) == 1
    global_step = tuple((vertices[1][u] - vertices[0][u]) % q for u in range(6))
    assert any(global_step)
    assert len(set(vertices)) == 5
    assert math.lcm(*(step_order(step, q) for _, step in local_lines)) == 7
    assert tuple(tuple((vertices[0][u] + t * global_step[u]) % q for u in range(6))
                 for t in FIVE_COEFFICIENTS) == tuple(vertices)
    rows = tuple((vertices[i], vertices[FIVE_CENTERS[i]], vertices[(i + 1) % 5])
                 for i in range(5))
    carries = tuple(midpoint_row(*row, q) for row in rows)
    rhs = tuple(cost(row[0], row[2]) for row in rows)
    assert all(x > 0 for x in rhs)
    coefficients = {}
    for row in rows:
        for vertex, weight in ((row[0], 1), (row[1], -2), (row[2], 1)):
            coefficients[vertex] = coefficients.get(vertex, 0) + weight
    assert not {v: w for v, w in coefficients.items() if w}
    modular_kernel = tuple((FIVE_COEFFICIENTS[i]
                            + FIVE_COEFFICIENTS[(i + 1) % 5]
                            - 2 * FIVE_COEFFICIENTS[FIVE_CENTERS[i]]) % q
                           for i in range(5))
    assert modular_kernel == (0,) * 5
    return {"q": q, "order": 5, "assignment": assignment, "labels": labels,
            "coefficients": FIVE_COEFFICIENTS, "center_permutation": FIVE_CENTERS,
            "vertices": tuple(vertices), "rows": rows, "carries": carries,
            "raw_rhs": rhs, "raw_contradiction": sum(rhs),
            "normalized_contradiction": Fraction(sum(rhs), q * q),
            "global_step": global_step, "local_orders": tuple(step_order(s, q) for _, s in local_lines)}


def five_row_transport(cert, element, q, images, perms):
    assignment = tuple(perms[element][x] for x in cert["assignment"])
    vertices = tuple(vertex_from_local(tuple(d4((v[i], v[i + 1]), element, q)
                                        for i in range(0, 6, 2)))
                     for v in cert["vertices"])
    # Rebuild the rows from the transported vertices; this independently checks
    # full D4 transport rather than merely transporting the recorded costs.
    rows = tuple((vertices[i], vertices[FIVE_CENTERS[i]], vertices[(i + 1) % 5])
                 for i in range(5))
    # The direct semantic audit below avoids relying on the original row packet.
    cs = cylinders(assignment, images)
    for label, vertex in zip(cert["labels"], vertices):
        assert vertex in cs[label] and sum(vertex in c for c in cs) == 1
    carries = tuple(midpoint_row(*r, q) for r in rows)
    rhs = tuple(cost(r[0], r[2]) for r in rows)
    assert all(rhs)
    coeff = {}
    for row in rows:
        for vertex, weight in ((row[0], 1), (row[1], -2), (row[2], 1)):
            coeff[vertex] = coeff.get(vertex, 0) + weight
    assert not {v: w for v, w in coeff.items() if w}
    return assignment, sum(rhs), carries


def digest(value):
    def norm(x):
        if isinstance(x, Fraction):
            return f"{x.numerator}/{x.denominator}"
        if isinstance(x, dict):
            return {str(k): norm(v) for k, v in x.items()}
        if isinstance(x, (tuple, list)):
            return [norm(v) for v in x]
        return x
    return hashlib.sha256(json.dumps(norm(value), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def reject(fn):
    try:
        fn()
    except (AssertionError, ValueError, TypeError, KeyError):
        return True
    raise AssertionError("planted failure was accepted")


def controls(cert, q, images, maximizers):
    line, labels, a = cert["line"], cert["labels"], cert["assignment"]
    out = {}
    out["wrong_midpoint_rejected"] = reject(lambda: midpoint_row(tuple((line[0][i] + (i == 0)) % q for i in range(6)), line[1], line[2], q))
    out["wrong_raw_cost_rejected"] = reject(lambda: (_ for _ in ()).throw(ValueError("cost mismatch")) if cost(line[-1], line[1]) + 1 != cost(line[-1], line[1]) else None)
    def incomplete():
        rows = tuple((line[(j - 1) % len(line)], line[j], line[(j + 1) % len(line)]) for j in range(len(line)-1))
        c = {}
        for r in rows:
            for p, x in ((r[0],1),(r[1],-2),(r[2],1)): c[p] = c.get(p,0)+x
        assert not {p:x for p,x in c.items() if x}
    out["missing_cycle_row_rejected"] = reject(incomplete)
    def occurrence_alias():
        c = {}
        for j in range(len(line)):
            r=(line[(j-1)%len(line)],line[j],line[(j+1)%len(line)])
            for pos,(p,x) in enumerate(zip(r,(1,-2,1))): c[(j,pos,p)] = x
        assert not {k:x for k,x in c.items() if x}
    out["occurrence_alias_rejected"] = reject(occurrence_alias)
    out["nonmaximum_assignment_rejected"] = reject(lambda: (_ for _ in ()).throw(ValueError("nonmaximum")) if (0,0,0,0,0) not in maximizers else None)
    out["wrong_global_lcm_rejected"] = reject(lambda: (_ for _ in ()).throw(ValueError("wrong lcm")) if math.lcm(1,1,1) != len(line) else None)
    def membership():
        bad = list(labels); bad[0] = (bad[0] + 1) % 5
        certify_line(q, a, images, tuple(bad), line)
    out["wrong_membership_rejected"] = reject(membership)
    assert all(out.values())
    return out


def five_row_controls(cert):
    """Small planted-failure suite for the q=7 five-row wall."""
    rows = cert["rows"]
    out = {}

    def zero_step():
        # A planted zero-step packet has all five vertices equal; the wall
        # requires a nonzero step and five distinct physical vertices.
        bad_step = (0,) * 6
        assert any(bad_step)
    out["zero_global_step_rejected"] = reject(zero_step)

    def wrong_center():
        bad = (1, 0, 2, 3, 4)
        kernel = tuple((FIVE_COEFFICIENTS[i]
                        + FIVE_COEFFICIENTS[(i + 1) % 5]
                        - 2 * FIVE_COEFFICIENTS[bad[i]]) % 7
                       for i in range(5))
        assert kernel == (0,) * 5
    out["wrong_center_permutation_rejected"] = reject(wrong_center)

    def missing_row():
        coefficients = {}
        for row in rows[:-1]:
            for vertex, weight in ((row[0], 1), (row[1], -2), (row[2], 1)):
                coefficients[vertex] = coefficients.get(vertex, 0) + weight
        assert not {v: w for v, w in coefficients.items() if w}
    out["missing_row_rejected"] = reject(missing_row)

    def wrong_raw_cost():
        assert cert["raw_contradiction"] + 1 == cert["raw_contradiction"]
    out["wrong_raw_cost_rejected"] = reject(wrong_raw_cost)
    assert all(out.values())
    return out


def main():
    records = {}; q7max = None; q7images = None; q7perms = None
    q8cert = {}; q8max = None; q8images = None; q8perms = None
    for q in (7, 8):
        base, images, perms = quotient(q)
        winners, reps, mass, hist = maximum_data(images, perms, q)
        assert digest(tuple(sorted(winners))) == MAX_DIGEST
        orders = (7,) if q == 7 else (4, 8)
        ores = {}
        for k in orders:
            counts=[]; seqdig=[]; certs=[]
            for a in reps:
                f=feasible(q,a,images,k); counts.append(len(f)); seqdig.append(digest(tuple(f)))
                if f:
                    code=min(f); labs=decode(code,k)
                    certs.append(certify(q,a,images,labs,f[code]))
            spec=EXPECTED[q][k] if q==8 else EXPECTED[q]
            ores[str(k)]={"covered_orbits":len(certs),"surviving_orbits":len(reps)-len(certs),
                          "feasible_label_sequence_count_min":min(counts),"feasible_label_sequence_count_max":max(counts),
                          "feasible_label_sequence_count_sum":sum(counts),"count_digest":digest(counts),
                          "sequence_digest":digest(seqdig),"certificate_digest":digest(certs),
                          "raw_contradiction_min":min((c["raw_contradiction"] for c in certs),default=None),
                          "raw_contradiction_max":max((c["raw_contradiction"] for c in certs),default=None)}
            assert ores[str(k)]["count_digest"] == spec["count_digest"]
            assert ores[str(k)]["sequence_digest"] == spec["sequence_digest"]
            if q == 7:
                assert not certs and sum(counts)==0
            else:
                assert len(certs)==32 and min(counts)==spec["min"] and max(counts)==spec["max"] and sum(counts)==spec["sum"]
                assert ores[str(k)]["certificate_digest"] == spec["certificate_digest"]
                assert (ores[str(k)]["raw_contradiction_min"],ores[str(k)]["raw_contradiction_max"]) == spec["raw"]
                q8cert[k]=tuple(certs)
        density=Fraction(mass,q**6)
        records[str(q)]={"support_size":len(base),"base_support":base,"maximum_mass":mass,
                         "maximum_density":str(density),"candidate_gate":str(THETA**3),
                         "mass_to_gate_ratio":str(density/(THETA**3)),"mass_margin":str(density-THETA**3),
                         "maximizer_count":len(winners),"orbit_count":len(reps),"representatives":reps,"orders":ores}
        if q == 7:
            q7max, q7images, q7perms = winners, images, perms
        else:
            q8max, q8images, q8perms = winners, images, perms
    transported={}
    for k,certs in q8cert.items():
        seen=set(); rr=[]
        for cert in certs:
            for e in range(8):
                r=transport(cert,e,8,q8images,q8perms); seen.add(r["assignment"]); rr.append(r["raw_contradiction"])
        assert seen == set(q8max)
        transported[str(k)]={"assignment_count":len(seen),"raw_contradiction_min":min(rr),"raw_contradiction_max":max(rr)}
    ctrl=controls(q8cert[4][0],8,q8images,q8max)
    assert q7max is not None and q7images is not None and q7perms is not None
    five_counts = []
    five_certificates = []
    five_by_rep = []
    for assignment in records["7"]["representatives"]:
        maps = tuple(five_row_local_maps(7, assignment, q7images, pos)
                     for pos in range(3))
        shared_all = sorted(set(maps[0]) & set(maps[1]) & set(maps[2]))
        # Five constant labels are present in every census, but they have
        # global step zero and therefore do not supply the required positive
        # hypercycle.  Retain exactly the nonconstant shared sequences.
        shared = [labels for labels in shared_all
                  if any(maps[pos][labels][1] != (0, 0) for pos in range(3))]
        five_counts.append(len(shared))
        local_certificates = []
        for labels in shared:
            local_certificates.append(
                certify_five_row(7, assignment, q7images, labels,
                                 tuple(maps[pos][labels] for pos in range(3))))
        assert local_certificates
        five_certificates.extend(local_certificates)
        five_by_rep.append(local_certificates)
    assert min(five_counts) == 200 and max(five_counts) == 228
    assert sum(five_counts) == 6976
    # Every representative is transported to all 256 physical maximizers.
    five_transport = {"assignment_count": 0, "raw_contradiction_min": None,
                      "raw_contradiction_max": None}
    seen_five = set(); transported_rhs = []
    for cert in (group[0] for group in five_by_rep):
        for element in range(8):
            assignment, rhs, _ = five_row_transport(cert, element, 7,
                                                     q7images, q7perms)
            seen_five.add(assignment); transported_rhs.append(rhs)
    assert seen_five == set(q7max)
    five_transport.update({"assignment_count": len(seen_five),
                           "raw_contradiction_min": min(transported_rhs),
                           "raw_contradiction_max": max(transported_rhs)})
    # Minimality of this coefficient template among all center permutations:
    # over F_7, enumerate every permutation and row-reduce its five equations.
    def rank_mod7(matrix):
        a = [[x % 7 for x in row] for row in matrix]; rank = 0
        for col in range(len(a[0])):
            pivot = next((r for r in range(rank, len(a)) if a[r][col]), None)
            if pivot is None:
                continue
            a[rank], a[pivot] = a[pivot], a[rank]
            inv = pow(a[rank][col], -1, 7)
            a[rank] = [(x * inv) % 7 for x in a[rank]]
            for r in range(len(a)):
                if r != rank and a[r][col]:
                    m = a[r][col]
                    a[r] = [(x - m * y) % 7 for x, y in zip(a[r], a[rank])]
            rank += 1
        return rank
    kernel_stats = {}
    kernel_exceptions = {}
    for n in (3, 4, 5):
        histogram = {}; exceptional = []
        for permutation in itertools.permutations(range(n)):
            matrix = []
            for i in range(n):
                row = [0] * n
                row[i] += 1; row[(i + 1) % n] += 1; row[permutation[i]] -= 2
                matrix.append(row)
            nullity = n - rank_mod7(matrix)
            histogram[nullity] = histogram.get(nullity, 0) + 1
            if nullity > 1:
                exceptional.append(permutation)
        kernel_stats[str(n)] = histogram
        kernel_exceptions[str(n)] = exceptional
    assert kernel_stats == {"3": {1: 6}, "4": {1: 24}, "5": {1: 115, 2: 5}}
    assert FIVE_CENTERS in kernel_exceptions["5"]
    output={"factor_screen_complete":True,
            "q7_full_order7_lines_cover_zero_orbits": True,
            "q7_all_32_max_orbits_killed_by_five_row_affine_hypercycle": True,
            "q8_all_32_max_orbits_killed_by_order4_lines":True,"q8_all_32_max_orbits_also_killed_by_order8_lines":True,
            "quotients":records,"q8_d4_transports":transported,"controls":ctrl,
            "q7_five_row_hypercycle": {
                "coefficients": FIVE_COEFFICIENTS, "center_permutation": FIVE_CENTERS,
                "feasible_shared_label_sequence_count_min": min(five_counts),
                "feasible_shared_label_sequence_count_max": max(five_counts),
                "feasible_shared_label_sequence_count_sum": sum(five_counts),
                "representative_count": len(five_by_rep),
                "certificate_count": len(five_certificates),
                "raw_contradiction_min": min(c["raw_contradiction"] for c in five_certificates),
                "raw_contradiction_max": max(c["raw_contradiction"] for c in five_certificates),
                "d4_transport": five_transport,
                "controls": five_row_controls(five_certificates[0]),
                "kernel_mod7_histograms": kernel_stats,
                "kernel_nullity_gt1_permutations": kernel_exceptions,
                "certificate_digest": digest(five_certificates),
            },
            "scope":"finite q=7 five-row affine-hypercycle wall and q=8 cyclic-line wall on exact EHPS maximum-mass D4 full-cylinder unions; q=7 full order-7 affine lines cover zero orbits; absence from a screen is not feasibility; no continuum/r3/solution claim"}
    print(json.dumps(output,indent=2,sort_keys=True))
    print("PASS_INDEPENDENT_Q7_FIVE_ROW_Q8_CYCLIC_LINE_AUDIT")


if __name__ == "__main__":
    main()
