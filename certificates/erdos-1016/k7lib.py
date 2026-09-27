"""Shared driver for the k = 7 extension of the Erdős #1016 certificate.

``pancyc.c`` is a C port of ``pancyclic.Search`` (same class order, parity
cycle forms, dead-state memo, target shortlist and branching order), so its
per-level node counts are comparable with RESULT.json at k = 6.  This module
builds it into a temporary directory -- never into the certificate directory,
which a replay must leave byte-identical -- and parses its output.

Also here: the explicit families G7(n) (7 chords; the class the search finds
at 110 <= n <= 113) and S8(n) (8 chords; the 8-chord witnesses of
witnesses_k7.json).
"""
import pathlib
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import pancyclic as pc  # noqa: E402

K7_SAT = range(109, 115)          # 7-chord pancyclic graphs exist here ...
K7_EXCLUDE = range(115, 216)      # ... and nowhere here; n >= 216 by capacity
K7_QUICK_EXCLUDE = range(150, 216)
K7_PYTHON = range(150, 216)       # levels re-decided class by class in Python ...
K7_PYTHON_QUICK = range(180, 216)  # ... and in the quick replay
G7_SKELETON = ((0, 2), (0, 11), (1, 6), (3, 8), (4, 10), (5, 9), (7, 12))
S8_SKELETON = ((0, 2), (0, 13), (1, 6), (3, 11), (4, 9), (5, 12), (7, 14), (8, 10))

_HEAD = re.compile(r"^(CLASSES|ORBITSUM) k=(\d+) (\d+)$|^MAXFORMS (\d+)$")
_LEVEL = re.compile(r"^LEVEL k=(\d+) n=(\d+) eligible=(\d+) eligible_labeled=(\d+) "
                    r"sat=(\d+) nodes=(\d+)")
_SAT = re.compile(r"^SAT n=(\d+) class=(\d+) t=(\d+) skel ([\d\- ]+) arcs ([\d ]+)$")
_CLASS = re.compile(r"^CLASS n=(\d+) class=(\d+) sat=([01]) nodes=(\d+) t=(\d+) skel ([\d\- ]+)$")


def g7_arcs(n):
    """Arc lengths of G7(n) on its 13-point skeleton; one arc grows with n."""
    return [1, 1, 1, 4, n - 60, 8, 1, 13, 2, 25, 1, 2, 1]


def g7(n):
    """The 7-chord family G7(n), n >= 61: pancyclic for every 61 <= n <= 113,
    and not at n = 114 (no cycle of length 61)."""
    return pc.realise(13, G7_SKELETON, g7_arcs(n))[1]


def s8_arcs(n):
    """Arc lengths of S8(n) on its 15-point skeleton; one arc grows with n."""
    return [1, 1, 1, 13, 1, 8, 1, 22, n - 107, 1, 50, 4, 1, 2, 1]


def s8(n):
    """The 8-chord family S8(n), n >= 108: pancyclic for every 108 <= n <= 186,
    and not at n = 187 (no cycle of length 108).  Its skeleton, a one-chord
    extension of G7's, was found by an exact search at n = 185."""
    return pc.realise(15, S8_SKELETON, s8_arcs(n))[1]


def python_decide(task):
    """Picklable worker: task = (t, skeleton, orders).  Re-decide one class with
    the Python reference at each order: [(pancyclic?, nodes), ...]."""
    t, skeleton, orders = task
    forms = pc.cycle_forms(t, skeleton)
    out = []
    for n in orders:
        x, nodes = pc.decide(t, skeleton, n, forms)
        out.append((x is not None, nodes))
    return out


def parse(text):
    out = {"classes": None, "orbit_sum": None, "max_forms": None, "levels": {}, "sat": [],
           "per_class": []}
    for line in text.splitlines():
        m = _HEAD.match(line)
        if m:
            if m.group(1) == "CLASSES":
                out["classes"] = int(m.group(3))
            elif m.group(1) == "ORBITSUM":
                out["orbit_sum"] = int(m.group(3))
            else:
                out["max_forms"] = int(m.group(4))
            continue
        m = _LEVEL.match(line)
        if m:
            out["levels"][int(m.group(2))] = {"eligible_classes": int(m.group(3)),
                                              "eligible_labeled": int(m.group(4)),
                                              "sat_classes": int(m.group(5)),
                                              "nodes": int(m.group(6))}
            continue
        m = _CLASS.match(line)
        if m:
            out["per_class"].append({
                "n": int(m.group(1)), "class": int(m.group(2)), "sat": m.group(3) == "1",
                "nodes": int(m.group(4)), "t": int(m.group(5)),
                "skeleton": tuple(tuple(int(v) for v in p.split("-")) for p in m.group(6).split())})
            continue
        m = _SAT.match(line)
        if m:
            skel = [[int(v) for v in p.split("-")] for p in m.group(4).split()]
            out["sat"].append({"n": int(m.group(1)), "class": int(m.group(2)),
                               "t": int(m.group(3)), "skeleton": skel,
                               "arcs": [int(v) for v in m.group(5).split()]})
    return out


class Engine:
    """pancyc.c, compiled into a private temporary directory."""

    def __init__(self):
        cc = shutil.which("cc") or shutil.which("gcc")
        if cc is None:
            raise RuntimeError("no C compiler (cc or gcc) on PATH")
        self._tmp = tempfile.TemporaryDirectory(prefix="erdos1016-k7-")
        self.exe = pathlib.Path(self._tmp.name) / "pancyc"
        subprocess.run([cc, "-O2", "-o", str(self.exe), str(HERE / "pancyc.c")], check=True)

    def run(self, k, lo, hi, mode="census", shard=None):
        argv = [str(self.exe), str(k), str(lo), str(hi), mode]
        if shard is not None:
            argv += [str(shard[0]), str(shard[1])]
        proc = subprocess.run(argv, capture_output=True, text=True, check=True)
        return parse(proc.stdout)

    def census(self, k, lo, hi, jobs, mode="census"):
        """Search every eligible class at every n in lo..hi, split into class
        shards (index mod jobs).  Memos are per class, so counts add up.
        mode "classes" also returns every class's verdict and node count."""
        jobs = max(1, jobs)
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            parts = list(ex.map(lambda r: self.run(k, lo, hi, mode, (r, jobs)),
                                range(jobs)))
        head = {(p["classes"], p["orbit_sum"], p["max_forms"]) for p in parts}
        if len(head) != 1:
            raise RuntimeError(f"shards disagree on the class census: {head}")
        merged = dict(parts[0])
        merged["levels"] = {n: {key: sum(p["levels"][n][key] for p in parts)
                                for key in parts[0]["levels"][n]}
                            for n in range(lo, hi + 1)}
        merged["sat"] = sorted((s for p in parts for s in p["sat"]),
                               key=lambda s: (s["n"], s["class"]))
        merged["per_class"] = sorted((c for p in parts for c in p["per_class"]),
                                     key=lambda c: (c["n"], c["class"]))
        return merged

    def one_class(self, k, lo, hi, index, nclasses):
        """Search a single class at every n in lo..hi (a one-class shard)."""
        return self.run(k, lo, hi, "census", (index, nclasses))

    def first(self, k, lo, hi):
        """Stop each n at the first pancyclic class (descending form count)."""
        return self.run(k, lo, hi, "first")
