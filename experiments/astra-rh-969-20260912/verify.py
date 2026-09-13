"""Standalone, read-only semantic checker of bounded generic countermodels.

No producer imports, solver, network, floats, RH hypothesis, or axiom audit.
The all-parameter argument is in RESULT.md, not proved by this checker.
"""
from fractions import Fraction

SCHEMA = "rh-generic-floor-countermodels-v1"
SCOPE = {"generic_coefficients": True, "mobius_coefficients": False,
         "rh_proved": False, "new_mobius_bound": False}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, label, minimum):
    require(type(value) is int and value >= minimum,
            label + " must be an exact integer >= " + str(minimum))
    return value


def verify_receipt(receipt):
    """Recompute canonical cells, signs, prefix bounds and rational errors."""
    require(type(receipt) is dict and set(receipt) == {"schema", "scope", "families"},
            "unexpected receipt fields")
    require(receipt["schema"] == SCHEMA, "wrong schema")
    scope = receipt["scope"]
    require(type(scope) is dict and set(scope) == set(SCOPE), "wrong scope fields")
    require(all(type(scope[k]) is bool and scope[k] is v for k, v in SCOPE.items()),
            "false theorem scope or nonboolean scope flag")
    families = receipt["families"]
    require(type(families) is list and 1 <= len(families) <= 16,
            "expected one through sixteen replay families")
    reports = []
    previous_h = 0
    for family in families:
        require(type(family) is dict and set(family) == {"h", "x", "bins"},
                "unexpected family fields")
        h = integer(family["h"], "h", 4)
        require(h % 4 == 0 and h <= 64 and h > previous_h,
                "h must increase, be divisible by four, and not exceed replay ceiling 64")
        previous_h = h
        x = integer(family["x"], "x", 1)
        require(x == h**5, "wrong scale x")
        cells = family["bins"]
        require(type(cells) is list and len(cells) == h // 4, "missing or extra bins")
        qs = list(range(h // 4, h // 2))
        # Independent reconstruction by direct division, not inverse square roots.
        groups = {q: [] for q in qs}
        for n in range(h*h, 2*h*h + 1):
            q = x // (n*n)
            if q in groups:
                groups[q].append(n)
        coefficients = {}
        correlation = Fraction(0)
        pair_bound = Fraction(0)
        for cell, q in zip(cells, qs):
            require(type(cell) is dict and set(cell) ==
                    {"q", "left", "right", "coefficients"}, "unexpected bin fields")
            require(integer(cell["q"], "q", 1) == q, "wrong or duplicate quotient")
            members = groups[q]
            require(bool(members), "empty expected quotient cell")
            require(integer(cell["left"], "left", 1) == members[0] and
                    integer(cell["right"], "right", 1) == members[-1],
                    "wrong cell endpoints")
            length = len(members)
            require(h // 2 <= length <= 4*h, "cell-width lemma failed")
            half = length // 2
            expected = [[n, 1] for n in members[:half]]
            expected += [[n, -1] for n in members[-half:]]
            rows = cell["coefficients"]
            require(type(rows) is list and len(rows) == 2*half, "wrong support size")
            for row in rows:
                require(type(row) is list and len(row) == 2, "bad coefficient row")
                integer(row[0], "coefficient index", 1)
                require(type(row[1]) is int and row[1] in (-1, 1), "bad coefficient")
            require(rows == expected, "coefficients do not realize the claimed balanced cells")
            for n, a in rows:
                require(n not in coefficients, "overlapping cells")
                coefficients[n] = a
            cell_sum = sum((Fraction(a * (x % (n*n)), n*n)
                            for n, a in rows), Fraction(0))
            lower = Fraction(half*half, 4*h)
            require(cell_sum >= lower, "signed phase lower bound failed")
            correlation += cell_sum
            pair_bound += lower
        prefix = 0
        max_prefix = 0
        for n in range(1, 2*h*h + 1):
            prefix += coefficients.get(n, 0)
            require(prefix*prefix <= 4*n, "square-root prefix envelope failed")
            max_prefix = max(max_prefix, abs(prefix))
        require(prefix == 0, "nonzero completed-block sum")
        floor_sum = sum(a * (x // (n*n)) for n, a in coefficients.items())
        require(floor_sum == 0, "balanced cell floors do not cancel")
        bound = Fraction(h*h, 256)
        require(correlation >= pair_bound >= bound, "global lower bound failed")
        reports.append({"h": h, "x": x, "bins_checked": len(cells),
                        "nonzero_coefficients": len(coefficients),
                        "prefix_positions_checked": 2*h*h,
                        "maximum_absolute_prefix": max_prefix,
                        "negative_error_lower_bound": str(bound),
                        "pair_bound": str(pair_bound), "floor_sum": floor_sum})
    return {"accepted": True, "scope": dict(SCOPE),
            "families_checked": len(reports),
            "bins_checked": sum(r["bins_checked"] for r in reports),
            "families": reports}

def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def main():
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path,
                        default=Path(__file__).with_name("receipt.json"))
    args = parser.parse_args()
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"),
                             object_pairs_hook=_unique_keys)
        result = verify_receipt(receipt)
    except (ValueError, OSError, RecursionError) as error:
        print(json.dumps({"accepted": False, "error": str(error)}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
