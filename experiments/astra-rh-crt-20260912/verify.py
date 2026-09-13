"""Independent direct-period replay. Never imports the divisor-formula producer."""
from fractions import Fraction


def _moments(primes, h):
    period = 1
    for p in primes:
        period *= p*p
    pattern = [int(all(n % (p*p) != 0 for p in primes)) for n in range(period)]
    allowed = sum(pattern)
    cycles, rem = divmod(h, period)
    count = cycles*allowed + sum(pattern[1:rem+1])
    total = 0
    second = 0
    for start in range(period):
        total += count
        second += count*count
        count += pattern[(start+rem+1) % period] - pattern[(start+1) % period]
    rho = Fraction(allowed, period)
    if total != h*allowed:
        raise ValueError("Independent sliding-window sum invariant failed")
    return rho, Fraction(second, period) - (h*rho)**2


def _keys(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise ValueError("Unexpected object fields")


def _integer(value):
    if type(value) is not int or value < 0 or value.bit_length() > 512:
        raise ValueError("Expected a nonnegative integer of at most 512 bits")


def _parameters(primes, h):
    _integer(h)
    if type(primes) is not list or len(primes) > 12:
        raise ValueError("Expected a canonical prime list of length at most 12")
    last, period = 1, 1
    for p in primes:
        if type(p) is not int or not last < p <= 97:
            raise ValueError("Primes must be strictly increasing integers in [2,97]")
        divisor = 2
        while divisor*divisor <= p:
            if p % divisor == 0:
                raise ValueError("Composite prime parameter")
            divisor += 1
        last = p
        period *= p*p
        if period > 100000:
            raise ValueError("Direct replay period exceeds 100000")
    return period


def verify_receipt(doc):
    _keys(doc, ("schema", "problem", "scope", "rh_proved", "case_count", "cases", "adverse_phase"))
    if (doc["schema"] != "squarefree-crt-phase-v1" or doc["problem"] != "P969"
            or doc["scope"] != "uniform-residue-phase-only" or doc["rh_proved"] is not False):
        raise ValueError("Wrong schema, problem, or mathematical scope")
    _integer(doc["case_count"])
    if type(doc["cases"]) is not list or not 1 <= len(doc["cases"]) <= 128:
        raise ValueError("Expected between 1 and 128 sampled cases")
    if doc["case_count"] != len(doc["cases"]):
        raise ValueError("Declared case count disagrees with records")
    previous = None
    for case in doc["cases"]:
        _keys(case, ("primes", "H", "density", "variance"))
        _parameters(case["primes"], case["H"])
        key = (tuple(case["primes"]), case["H"])
        if previous is not None and key <= previous:
            raise ValueError("Cases must be unique and canonically sorted")
        previous = key
        rho, value = _moments(case["primes"], case["H"])
        if case["density"] != str(rho) or case["variance"] != str(value):
            raise ValueError("Claimed moments disagree with direct period enumeration")
        if value < 0 or value*value > case["H"]:
            raise ValueError("Sampled phase-variance bound failed")
    adverse = doc["adverse_phase"]
    _keys(adverse, ("primes", "H", "start", "count", "squared_error"))
    period = _parameters(adverse["primes"], adverse["H"])
    _integer(adverse["start"])
    _integer(adverse["count"])
    if not 1 <= adverse["H"] <= period or adverse["start"] >= period:
        raise ValueError("Adverse phase exceeds the bounded one-period replay domain")
    ps, h, start = adverse["primes"], adverse["H"], adverse["start"]
    count = sum(all((start+j) % (p*p) for p in ps) for j in range(1,h+1))
    rho, _ = _moments(ps, 0)
    squared = (count-h*rho)**2
    if adverse["count"] != count or adverse["squared_error"] != str(squared):
        raise ValueError("Adverse-phase calculation is false")
    if count != 0 or squared*squared <= h:
        raise ValueError("The selected phase does not demonstrate the claimed averaging gap")
    return dict(passed=True, case_count=len(doc["cases"]),
                distinct_prime_sets=len({tuple(c["primes"]) for c in doc["cases"]}),
                sampled_phase_bounds_checked=True, adverse_phase_verified=True,
                scope="uniform-residue-phase-only", rh_proved=False)


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _parse_integer(text):
    if len(text.lstrip("-")) > 160:
        raise ValueError("JSON integer exceeds replay budget")
    return int(text)


def _no_float(text):
    raise ValueError("Floating-point JSON values are not permitted")


def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt")
    args = parser.parse_args()
    try:
        with open(args.receipt, "rb") as stream:
            raw = stream.read(262145)
        if len(raw) > 262144:
            raise ValueError("Receipt exceeds 256 KiB")
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_keys,
                         parse_int=_parse_integer, parse_float=_no_float,
                         parse_constant=_no_float)
        verdict = verify_receipt(doc)
    except (OSError, ValueError, RecursionError) as error:
        print(json.dumps(dict(passed=False, error=str(error)), sort_keys=True))
        return 1
    print(json.dumps(verdict, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
