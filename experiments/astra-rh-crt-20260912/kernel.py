"""Positive divisor formula for finite-prime, uniform-phase variance."""
from fractions import Fraction
from math import isqrt

MAX_PRIMES = 12
MAX_PRIME = 97
MAX_BITS = 512


def _validate_primes(primes):
    if type(primes) not in (list, tuple) or len(primes) > MAX_PRIMES:
        raise ValueError("Expected at most 12 primes in a list or tuple")
    previous = 1
    for p in primes:
        if type(p) is not int or not previous < p <= MAX_PRIME:
            raise ValueError("Primes must be strictly increasing integers in [2,97]")
        if any(p % d == 0 for d in range(2, isqrt(p) + 1)):
            raise ValueError("Composite modulus is not a prime")
        previous = p


def _validate_length(h):
    if type(h) is not int or h < 0 or h.bit_length() > MAX_BITS:
        raise ValueError("H must be a nonnegative integer of at most 512 bits")


def variance(primes, h):
    _validate_primes(primes)
    _validate_length(h)
    return phase_kernel(primes, h)


def phase_kernel(primes, h):
    """Algebraic real-parameter extension; variance only for integer H."""
    _validate_primes(primes)
    if type(h) not in (int, Fraction) or h < 0:
        raise ValueError("Kernel parameter must be a nonnegative exact rational")
    h = Fraction(h)
    if max(h.numerator.bit_length(), h.denominator.bit_length()) > MAX_BITS:
        raise ValueError("Kernel parameter exceeds the 512-bit replay budget")
    terms = [(1, Fraction(1))]
    for p in primes:
        factor = Fraction(p * p - 2, p * p)
        terms = [(d, weight * factor) for d, weight in terms] + [
            (d * p, weight) for d, weight in terms]
    result = Fraction()
    for d, weight in terms:
        fraction = Fraction(h % (d * d), d * d)
        result += weight * fraction * (1 - fraction)
    return result


def _density(primes):
    result = Fraction(1)
    for p in primes:
        result *= 1 - Fraction(1, p*p)
    return result


def refinement_energy(small, large, h):
    """Uniform-phase L2 increment after normalizing each sieve by its density."""
    _validate_primes(small)
    _validate_primes(large)
    _validate_length(h)
    if not set(small).issubset(large):
        raise ValueError("Prime sets must be nested")
    return variance(large, h) / _density(large)**2 - variance(small, h) / _density(small)**2


def build_receipt():
    """Fixed test cohort, not a certificate of an asymptotic estimate."""
    prime_sets = ([], [2], [3], [2,3], [2,5], [3,5], [2,3,5])
    lengths = (0,1,2,3,4,9,16,36,900,10**30+2)
    cases = [dict(primes=ps, H=h, density=str(_density(ps)), variance=str(variance(ps,h)))
             for ps in prime_sets for h in lengths]
    cases.sort(key=lambda row: (tuple(row["primes"]), row["H"]))
    primes = [2,3,5]
    period = 1
    for p in primes:
        period *= p*p
    start = sum((-j)*(period//(p*p))*pow(period//(p*p),-1,p*p)
                for j,p in enumerate(primes,1)) % period
    h = len(primes)
    count = sum(all((start+j) % (p*p) for p in primes) for j in range(1,h+1))
    adverse = dict(primes=primes,H=h,start=start,count=count,
                   squared_error=str((count-h*_density(primes))**2))
    return dict(schema="squarefree-crt-phase-v1",problem="P969",
                scope="uniform-residue-phase-only",rh_proved=False,
                case_count=len(cases),cases=cases,adverse_phase=adverse)


def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", required=True, help="Create a NEW receipt; never overwrite")
    args = parser.parse_args()
    receipt = build_receipt()
    try:
        with open(args.emit,"x",encoding="utf-8") as stream:
            json.dump(receipt,stream,indent=2,sort_keys=True)
            stream.write("\n")
    except OSError as error:
        parser.exit(2,str(error)+"\n")
    print(json.dumps(dict(emitted=args.emit,case_count=receipt["case_count"],
                          scope=receipt["scope"]),sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
