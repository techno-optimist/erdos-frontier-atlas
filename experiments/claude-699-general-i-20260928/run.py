"""Run the C engine in J shards and add the shards up.

  python3 -I run.py I X J [--exe PATH]     # prints one JSON line

The shards split the smooth S_0 (and the central n) by index modulo J, so their special counts,
checksums and candidate counts add up to those of the unsharded run.
"""
import json
import pathlib
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
MASK = (1 << 64) - 1


def build(out=None):
    """Compile search699.c; returns the executable path."""
    out = pathlib.Path(out or HERE / "search699")
    subprocess.run(["cc", "-O2", "-o", str(out), str(HERE / "search699.c"), "-lm"], check=True)
    return out


def parse(text):
    stats, surv, special = None, [], []
    for line in text.splitlines():
        f = line.split()
        if f and f[0] == "stats":
            stats = [int(v) for v in f[3:8]]
        elif f and f[0] == "survivor":
            surv.append([int(v) for v in f[1:]])
        elif f and f[0] == "special":
            special.append([int(v) for v in f[1:]])
    if stats is None:
        raise RuntimeError("engine printed no stats line")
    return stats, surv, special


def engine(exe, i, X, *extra):
    p = subprocess.run([str(exe), str(i), str(X), *map(str, extra)], capture_output=True, text=True, check=True)
    return parse(p.stdout)


def run(exe, i, X, J):
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=J) as ex:
        parts = list(ex.map(lambda k: engine(exe, i, X, "--shard", f"{k}/{J}"), range(J)))
    return {"i": i, "X": X,
            "special": sum(p[0][0] for p in parts),
            "checksum": sum(p[0][1] for p in parts) & MASK,
            "cand12": sum(p[0][2] for p in parts),
            "central": sum(p[0][3] for p in parts),
            "survivors": sorted(s for p in parts for s in p[1]),
            "seconds": round(time.time() - t0, 1), "jobs": J}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--exe")]
    exe = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--exe=")), None) or build()
    i, X, J = int(args[0]), int(float(args[1])), int(args[2])
    print(json.dumps(run(exe, i, X, J)), flush=True)
