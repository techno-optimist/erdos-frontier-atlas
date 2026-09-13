"""Exact square-divisor transforms; no RH or Mobius bound is assumed."""
from bisect import bisect_right
from math import isqrt


def _integer(value, name, minimum):
    if type(value) is not int or value < minimum:
        raise ValueError(name + " must be an integer >= " + str(minimum))
    return value


def hyperbola_sum(coefficients, x, cutoff):
    """Evaluate sum a[n]*floor(x/n**2) by an exact hyperbola split."""
    _integer(x, "x", 0)
    _integer(cutoff, "cutoff", 1)
    if type(coefficients) is not dict:
        raise ValueError("coefficients must be a dictionary")
    for n, a in coefficients.items():
        _integer(n, "coefficient index", 1)
        if type(a) is not int:
            raise ValueError("coefficients must be exact integers")
    indices = sorted(coefficients)
    prefixes = [0]
    for n in indices:
        prefixes.append(prefixes[-1] + coefficients[n])

    def partial(t):
        return prefixes[bisect_right(indices, t)]

    head = sum(a * (x // (n * n))
               for n, a in coefficients.items() if n <= cutoff)
    k = x // (cutoff * cutoff)
    return head + sum(partial(isqrt(x // m)) - partial(cutoff)
                      for m in range(1, k + 1))

def make_family(h):
    """Produce one balanced-cell example, not Mobius coefficients.

    h <= 64 is a resource ceiling for this replay tool, not the theorem.
    """
    _integer(h, "h", 4)
    if h % 4 or h > 64:
        raise ValueError("replay requires h divisible by 4 with 4 <= h <= 64")
    x = h ** 5
    bins = []
    for q in range(h // 4, h // 2):
        left = isqrt(x // (q + 1)) + 1
        right = isqrt(x // q)
        half = (right - left + 1) // 2
        rows = [[n, 1] for n in range(left, left + half)]
        rows += [[n, -1] for n in range(right - half + 1, right + 1)]
        bins.append({"q": q, "left": left, "right": right,
                     "coefficients": rows})
    return {"h": h, "x": x, "bins": bins}

def main():
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, required=True,
                        help="new receipt path; existing files are never overwritten")
    parser.add_argument("--h", type=int, nargs="+", default=[4, 8, 12, 16, 24, 32])
    args = parser.parse_args()
    try:
        if not 1 <= len(args.h) <= 16 or args.h != sorted(set(args.h)):
            raise ValueError("parameters must be strictly increasing, with at most sixteen cases")
        receipt = {"schema": "rh-generic-floor-countermodels-v1",
                   "scope": {"generic_coefficients": True, "mobius_coefficients": False,
                             "rh_proved": False, "new_mobius_bound": False},
                   "families": [make_family(h) for h in args.h]}
        with args.emit.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(receipt, indent=2) + "\n")
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps({"emitted_families": len(receipt["families"]),
                      "path": str(args.emit), "rh_proved": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
