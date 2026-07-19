#!/usr/bin/env python3
"""Validate atlas/gap_map.json (Records lane) against its contract. Dependency-free.

Checks, all hard failures unless marked WARN:
  1. top-level shape: schema tag, note, entries list;
  2. every entry: exact key set, enum fields, bound structure ({value,source,year} or null);
  3. every entry.problem exists in atlas/stubs.json (WARN if entry.oeis not among that stub's refs);
  4. kind consistency: value_gap => both bounds; bounded_below_only => lower only;
     bounded_above_only => upper only; not_gap_shaped => no bounds AND witness_side none;
     verified_range => lower present;
  5. witness_side none => witness_feasibility none;
  6. every numeric bound carries a non-empty source; provenance.checked non-empty;
  7. (problem, quantity) unique;
  8. epistemic ledger (WS7): evidence[] items are well-formed ({type,artifact,date},
     type in the enum, non-empty strings);
  9. epistemic ledger (WS7): the stored confidence class EQUALS the class computed
     from evidence[] (see compute_confidence below); an entry may not carry
     confidence without evidence, nor evidence without a stored confidence.
Exit 0 iff everything holds.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRY_KEYS = {"problem", "oeis", "quantity", "kind", "lower", "upper", "witness_side",
              "witness_object", "witness_verifier", "witness_feasibility",
              "exact_feasibility", "status", "notes", "provenance"}
# WS7 epistemic-ledger fields: optional in the schema (additive extension), but if either
# is present the pair must be present and consistent (checked in check_ledger).
OPTIONAL_KEYS = {"evidence", "confidence"}
KINDS = {"value_gap", "next_cell", "bounded_below_only", "bounded_above_only",
         "verified_range", "not_gap_shaped"}
SIDES = {"lower", "upper", "both", "none"}
FEAS = {"open-easy", "plausible", "hard", "historic", "none"}
EXACT = {"cell", "drat-candidate", "wall", "unknown"}
STATUS = {"open", "record_in_progress", "closed"}
EVIDENCE_TYPES = {"formal_proof", "implementation", "replay_receipt",
                  "numeric_scan", "literature"}
CONFIDENCE_CLASSES = {"C0", "C1", "C2", "C3"}


def fail(errors, msg):
    errors.append(msg)


def compute_confidence(evidence):
    """Mechanical confidence class from recorded evidence (charter WS7). The rule:

      C0  iff any item has type formal_proof (a machine-checked formal proof
           dominates everything else);
      C1  iff >= 2 items of type implementation or replay_receipt with DISTINCT
           artifact strings (independent replications at the claimed range);
      C2  iff exactly 1 distinct implementation/replay_receipt artifact (a single
           verified, replayable implementation — two items citing the SAME
           artifact still count as one);
      C3  otherwise (numeric_scan / literature / no evidence — conjecture-grade
           numerics or literature-transcribed values, no independent artifact).

    The stored "confidence" field must EQUAL this computed value — the class is
    derived, never asserted.
    """
    types = [it.get("type") for it in evidence]
    if "formal_proof" in types:
        return "C0"
    artifacts = {it.get("artifact") for it in evidence
                 if it.get("type") in ("implementation", "replay_receipt")}
    if len(artifacts) >= 2:
        return "C1"
    if len(artifacts) == 1:
        return "C2"
    return "C3"


def check_ledger(errors, tag, e):
    """WS7 ledger checks on one entry: evidence[] shape + stored-vs-computed class."""
    has_ev, has_conf = "evidence" in e, "confidence" in e
    if has_conf and not has_ev:
        fail(errors, f"{tag}: confidence present but no evidence[] — a class must be "
                     f"computable from recorded evidence")
        return
    if has_ev and not has_conf:
        fail(errors, f"{tag}: evidence[] present but no stored confidence — stamp the "
                     f"computed class")
        return
    if not has_ev:
        return
    ev = e["evidence"]
    if not isinstance(ev, list) or not ev:
        fail(errors, f"{tag}: evidence must be a non-empty list")
        return
    ok = True
    for j, it in enumerate(ev):
        if not isinstance(it, dict) or set(it) != {"type", "artifact", "date"}:
            fail(errors, f"{tag}.evidence[{j}]: item must be exactly {{type,artifact,date}}")
            ok = False
            continue
        if it["type"] not in EVIDENCE_TYPES:
            fail(errors, f"{tag}.evidence[{j}]: bad type {it['type']!r}")
            ok = False
        for fld in ("artifact", "date"):
            if not (isinstance(it[fld], str) and it[fld].strip()):
                fail(errors, f"{tag}.evidence[{j}]: {fld} must be a non-empty string")
                ok = False
    if e["confidence"] not in CONFIDENCE_CLASSES:
        fail(errors, f"{tag}: bad confidence {e['confidence']!r}")
        return
    if ok:
        computed = compute_confidence(ev)
        if e["confidence"] != computed:
            fail(errors, f"{tag}: stored confidence {e['confidence']} != computed "
                         f"{computed} — the class is derived from evidence[], "
                         f"never asserted")


def check_bound(errors, tag, b):
    if b is None:
        return
    if not isinstance(b, dict) or set(b) != {"value", "source", "year"}:
        fail(errors, f"{tag}: bound must be null or {{value,source,year}}")
        return
    if not (isinstance(b["value"], str) and b["value"].strip()):
        fail(errors, f"{tag}: bound value must be a non-empty string")
    if not (isinstance(b["source"], str) and b["source"].strip()):
        fail(errors, f"{tag}: bound source must be a non-empty string")
    if not (b["year"] is None or isinstance(b["year"], int)):
        fail(errors, f"{tag}: bound year must be int or null")


def main():
    errors, warns = [], []
    gm = json.loads((ROOT / "atlas" / "gap_map.json").read_text())
    stubs = json.loads((ROOT / "atlas" / "stubs.json").read_text())
    by_id = {r["id"]: r for r in stubs["problems"]}

    if gm.get("schema") != "erdos-gap-map-v1":
        fail(errors, "top: schema must be 'erdos-gap-map-v1'")
    if not isinstance(gm.get("note"), str) or not gm["note"].strip():
        fail(errors, "top: note required")
    entries = gm.get("entries")
    if not isinstance(entries, list) or not entries:
        fail(errors, "top: entries must be a non-empty list")
        entries = []

    seen = set()
    for i, e in enumerate(entries):
        tag = f"entry[{i}] (problem {e.get('problem', '?')})"
        missing = ENTRY_KEYS - set(e)
        extra = set(e) - ENTRY_KEYS - OPTIONAL_KEYS
        if missing or extra:
            fail(errors, f"{tag}: keys must be the contract set (+ optional "
                         f"{sorted(OPTIONAL_KEYS)}) (missing {missing}, extra {extra})")
            continue
        pid = e["problem"]
        if not isinstance(pid, int) or pid not in by_id:
            fail(errors, f"{tag}: problem id not in stubs.json")
        elif e["oeis"] is not None and e["oeis"] not in (by_id[pid].get("oeis") or []):
            warns.append(f"{tag}: oeis {e['oeis']} not among stub's refs (ok if better-sourced)")
        if e["oeis"] is not None and not (isinstance(e["oeis"], str) and len(e["oeis"]) == 7
                                          and e["oeis"][0] == "A" and e["oeis"][1:].isdigit()):
            fail(errors, f"{tag}: oeis must match A###### or null")
        if e["kind"] not in KINDS:
            fail(errors, f"{tag}: bad kind {e['kind']!r}")
        if e["witness_side"] not in SIDES:
            fail(errors, f"{tag}: bad witness_side")
        if e["witness_feasibility"] not in FEAS:
            fail(errors, f"{tag}: bad witness_feasibility")
        if e["exact_feasibility"] not in EXACT:
            fail(errors, f"{tag}: bad exact_feasibility")
        if e["status"] not in STATUS:
            fail(errors, f"{tag}: bad status")
        for fld in ("quantity", "witness_object", "witness_verifier", "notes"):
            if not (isinstance(e[fld], str) and e[fld].strip()):
                fail(errors, f"{tag}: {fld} must be a non-empty string")
        check_bound(errors, f"{tag}.lower", e["lower"])
        check_bound(errors, f"{tag}.upper", e["upper"])

        k, lo, up = e["kind"], e["lower"], e["upper"]
        if k == "value_gap" and (lo is None or up is None):
            fail(errors, f"{tag}: value_gap requires BOTH bounds")
        if k == "bounded_below_only" and (lo is None or up is not None):
            fail(errors, f"{tag}: bounded_below_only requires lower only")
        if k == "bounded_above_only" and (up is None or lo is not None):
            fail(errors, f"{tag}: bounded_above_only requires upper only")
        if k == "verified_range" and lo is None:
            fail(errors, f"{tag}: verified_range requires lower (= verified-through value)")
        if k == "not_gap_shaped" and (lo is not None or up is not None or e["witness_side"] != "none"):
            fail(errors, f"{tag}: not_gap_shaped requires no bounds and witness_side none")
        if e["witness_side"] == "none" and e["witness_feasibility"] != "none":
            fail(errors, f"{tag}: witness_side none requires witness_feasibility none")

        prov = e["provenance"]
        if (not isinstance(prov, dict) or set(prov) != {"added_by", "date", "checked"}
                or not prov.get("added_by") or not prov.get("date")
                or not isinstance(prov.get("checked"), list) or not prov["checked"]):
            fail(errors, f"{tag}: provenance must carry added_by, date, non-empty checked[]")

        check_ledger(errors, tag, e)

        key = (pid, e["quantity"])
        if key in seen:
            fail(errors, f"{tag}: duplicate (problem, quantity)")
        seen.add(key)

    for w in warns:
        print(f"  WARN: {w}")
    if errors:
        for m in errors:
            print(f"  FAIL: {m}")
        print(f"gap_map INVALID: {len(errors)} error(s), {len(entries)} entrie(s)")
        return 1
    counts = {}
    for e in entries:
        counts[e["witness_feasibility"]] = counts.get(e["witness_feasibility"], 0) + 1
    conf = {}
    for e in entries:
        conf[e.get("confidence", "unstamped")] = conf.get(e.get("confidence", "unstamped"), 0) + 1
    conf = {k: conf[k] for k in sorted(conf)}
    print(f"gap_map VALID: {len(entries)} entries; witness_feasibility {counts}; "
          f"confidence {conf}; {len(warns)} warn(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
