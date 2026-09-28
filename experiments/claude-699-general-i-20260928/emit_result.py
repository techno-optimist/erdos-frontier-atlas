#!/usr/bin/env python3
"""Write RESULT.json for the general-i P699 search. Refuses to overwrite an existing file.

  python3 -I emit_result.py OUT [--jobs J]            # runs the whole campaign (hours)
  python3 -I emit_result.py OUT --from-logs LOG...    # assembles rows already logged by run.py

Rows are {i, X, special, checksum, cand12, central, survivors, seconds, jobs}. The checkpoints
(i <= 10 at 1e11, i = 11..13 at 1e9) and the frontier windows are always recomputed here.
"""
import hashlib
import json
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run as R  # noqa: E402

CAMPAIGN = [(3, 10 ** 18), (4, 10 ** 18), (5, 10 ** 18), (6, 10 ** 17), (7, 10 ** 17),
            (8, 10 ** 15), (9, 10 ** 15), (10, 10 ** 15),
            (11, 10 ** 12), (12, 10 ** 12), (13, 10 ** 12)]
CHECKPOINTS = [(i, 10 ** 11) for i in range(3, 11)] + [(i, 10 ** 9) for i in range(11, 14)]
WINDOW = 10 ** 13          # frontier window above each searched bound
LEAST = 3


def main():
    args = sys.argv[1:]
    out = pathlib.Path(args[0])
    if out.exists():
        sys.exit(f"{out} exists; refusing to overwrite evidence")
    jobs = next((int(a.split("=", 1)[1]) for a in args if a.startswith("--jobs=")), 4)
    logs = args[args.index("--from-logs") + 1:] if "--from-logs" in args else []
    logged = {}
    for log in logs:
        for line in pathlib.Path(log).read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                logged[(row["i"], row["X"])] = row
    with tempfile.TemporaryDirectory() as tmp:
        exe = R.build(pathlib.Path(tmp) / "search699")
        runs = [logged.get((i, X)) or R.run(exe, i, X, jobs) for i, X in CAMPAIGN]
        checkpoints = [R.run(exe, i, X, jobs) for i, X in CHECKPOINTS]
        frontier = []
        for i, X in CAMPAIGN:
            count, special, surv = R.window(exe, i, X, X + WINDOW, jobs)
            frontier.append({"i": i, "from": X, "to": X + WINDOW, "special_in_window": count,
                             "least": special[:LEAST], "survivors": surv})
    src = (HERE / "search699.c").read_bytes()
    res = {"engine": "search699.c", "engine_sha256": hashlib.sha256(src).hexdigest(),
           "claim": "for each row, no pair (n, j) with n <= X passes (*) at every prime p >= i of "
                    "C(n, i); by Theorem 2 no counterexample to #699 with that i has n <= X",
           "runs": runs, "checkpoints": checkpoints, "frontier": frontier}
    assert all(r["survivors"] == [] for r in runs + checkpoints)
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
