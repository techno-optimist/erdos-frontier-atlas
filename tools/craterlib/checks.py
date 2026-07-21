#!/usr/bin/env python3
"""Machine checks + the WS7 quantities ledger gate.

Machine-checked roots and edges NAME a script; the validator EXECUTES it and
requires exit 0 before the crater is considered valid. The check ORDER is
contractual -- it is serialized into computed_statuses.json["machine_checks"]:
root certificate, then that root's supplementary checks in order, for each root
in graph order; then machine-checked edges in graph order.

The quantities ledger reuses tools/validate_gap_map.py's compute_confidence (the
WS7 C0-C3 ladder) rather than forking it, so the crater ledger and the Records
gap map can never drift into two different definitions of "C1".
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from .spec import failer

# Anchored on THIS package's location, not on spec.root: the bridge must keep
# working when a caller re-points a crater's root at a scratch directory.
_GAP_MAP = Path(__file__).resolve().parent.parent / "validate_gap_map.py"


def gap_map_module():
    spec = importlib.util.spec_from_file_location("validate_gap_map", _GAP_MAP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def collect_checks(g):
    checks = []
    for r in g["roots"]:
        checks.append((f"root:{r['node']}", r["certificate"]))
        for i, extra in enumerate(r.get("supplementary_checks", [])):
            checks.append((f"root:{r['node']}:supplementary[{i}]", extra))
    for e in g["edges"]:
        if e.get("machine_check"):
            checks.append((f"edge:{e['from']}->{e['to']}", e["machine_check"]))
    return checks


def run_machine_checks(spec, g):
    fail = failer(spec.label)
    results = []
    for label, script in collect_checks(g):
        path = spec.root / script
        if not path.exists():
            fail(f"machine check {label}: script missing: {script}")
        proc = subprocess.run([sys.executable, str(path)],
                              capture_output=True, text=True)
        results.append({"check": label, "script": script,
                        "exit": proc.returncode})
        if proc.returncode != 0:
            fail(f"machine check {label} FAILED (exit {proc.returncode}):\n"
                 f"{proc.stdout}\n{proc.stderr}")
    return results


def check_reach_license(spec, checks):
    """A level in the `full` role asserts a mathematical REACH (JC's "all n >= 3"
    is licensed by the stabilization lift, not by propagation). If it declares a
    reach_license, that artifact must be among the machine checks we just RAN --
    so the claim in the name is traceable to a passing check, not free text."""
    lic = spec.level(spec.full).reach_license
    if not lic:
        return
    scripts = {c["script"] for c in checks}
    if lic not in scripts:
        failer(spec.label)(
            f"level {spec.full}: reach_license {lic} is not among the executed "
            "machine checks -- the level's stated reach is unlicensed")


def check_quantities(spec):
    """Stored confidence class must EQUAL the one computed from evidence[]."""
    fail = failer(spec.label)
    if not spec.quantities_path.exists():
        if not spec.quantities_required:
            return 0
        fail(f"quantities ledger missing: {spec.quantities_path.name} (the WS7 "
             "confidence gate cannot be silently disabled by deleting the file)")
    q = json.loads(spec.quantities_path.read_text())
    gap = gap_map_module()
    seen = set()
    for e in q["entries"]:
        tag = e.get("id", "?")
        for field in ("id", "quantity", "kind", "status", "notes", "provenance"):
            if not str(e.get(field, "")).strip():
                fail(f"quantity {tag}: missing {field}")
        if tag in seen:
            fail(f"quantity {tag}: duplicate id")
        seen.add(tag)
        # bool is a subclass of int -- reject it explicitly so True/False can't
        # masquerade as a bracket endpoint.
        lo, hi = e.get("lower"), e.get("upper")
        if not (type(lo) is int and type(hi) is int and lo <= hi):
            fail(f"quantity {tag}: bad bracket [{lo!r}, {hi!r}]")
        ev = e.get("evidence", [])
        if not ev:
            fail(f"quantity {tag}: no evidence[]")
        for item in ev:
            # Crater evidence schema is exactly {type, artifact, note} -- note
            # carries the human-readable justification (richer than gap_map's
            # {type, artifact, date}); the confidence rule only reads type +
            # artifact, so the two ledgers share compute_confidence.
            if set(item) != spec.evidence_keys:
                fail(f"quantity {tag}: evidence item keys must be exactly "
                     "{" + ", ".join(sorted(spec.evidence_keys)) + "}, "
                     f"got {sorted(item)}")
            if item["type"] not in gap.EVIDENCE_TYPES:
                fail(f"quantity {tag}: bad evidence type {item['type']}")
            for fld in sorted(spec.evidence_keys - {"type"}):
                if not str(item[fld]).strip():
                    fail(f"quantity {tag}: evidence item missing {fld}")
        # replay_receipt / implementation artifacts must name a file that exists
        # and (if executable) passes -- a receipt may not cite a script that is
        # absent or that does not certify what the item claims.
        for item in ev:
            if item.get("type") in ("replay_receipt", "implementation"):
                art = item["artifact"].split()[0]
                if art.endswith(".py"):
                    p = spec.root / art
                    if not p.exists():
                        fail(f"quantity {tag}: evidence cites missing script {art}")
        computed = gap.compute_confidence(ev)
        if e.get("confidence") != computed:
            fail(f"quantity {tag}: stored confidence {e.get('confidence')} != "
                 f"computed {computed} (the class is derived, never asserted)")
    return len(q["entries"])
