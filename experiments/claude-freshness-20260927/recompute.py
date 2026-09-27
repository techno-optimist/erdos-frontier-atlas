#!/usr/bin/env python3
"""Recompute the mechanical half of this overlay from a local upstream YAML.

  python3 experiments/claude-freshness-20260927/recompute.py PATH/TO/problems.yaml

PATH must be teorth/erdosproblems data/problems.yaml at the pinned commit
(af83692edd2aee68d512e04fb7b9b9c175a29bb0).  The script compares every
strike-board surface's upstream status as frozen in atlas/stubs.json with the
YAML, and checks the result against strike-board.json.  It reads only; it
never writes.  PyYAML is required, as for tools/build_stubs.py.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    import yaml
    upstream = {int(p["number"]): p["status"]["state"]
                for p in yaml.safe_load(pathlib.Path(sys.argv[1]).read_text())}
    stubs = {r["id"]: r for r in json.loads((ROOT / "atlas" / "stubs.json").read_text())["problems"]}
    board = json.loads((HERE / "strike-board.json").read_text())
    bad = 0
    for s in board["surfaces"]:
        pid = s["problem"]
        want = (stubs[pid]["upstream_state_raw"], upstream[pid])
        got = (s["atlas_snapshot_upstream"], s["upstream_now"])
        if want != got:
            bad += 1
            print(f"MISMATCH #{pid}: overlay {got} vs recomputed {want}")
    changed = sum(1 for s in board["surfaces"] if s["atlas_snapshot_upstream"] != s["upstream_now"])
    print(f"{len(board['surfaces'])} surfaces checked, {changed} with an upstream status change, "
          f"{bad} mismatch(es)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
