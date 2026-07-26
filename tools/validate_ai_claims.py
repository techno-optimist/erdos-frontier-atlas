#!/usr/bin/env python3
"""Validate the AI-claim overlay, and enforce the one rule that makes it safe.

The overlay records that third parties have publicly claimed AI-assisted
resolutions of certain Erdos problems. It is a CLAIM FEED, not a status source.

The rule it exists to protect: **a claim never changes a status.** A status
changes when the upstream record changes. This atlas learned that on #552, where
its own "new value" claim had to be retracted after the fact, and applies it to
#421, where a circulating solution left the upstream record open. An overlay that
quietly promoted "someone says it's solved" into "it is solved" would be the
single most damaging thing this file could do, so that promotion is checked
here rather than left to good intentions.

Exit 0 iff the overlay is well formed AND no entry has been allowed to move a
status.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "atlas" / "ai_claims.json"
STUBS = ROOT / "atlas" / "stubs.json"

ALLOWED_VERDICTS = {
    "not independently checked",   # the default; we have not looked
    "verified",                    # we replayed it and it holds
    "refuted",                     # we replayed it and it does not
    "convention-dependent",        # true under one reading, false under another
    "unreproducible",              # we tried and could not obtain the artifacts
}


def main() -> int:
    errors = []
    doc = json.loads(OVERLAY.read_text(encoding="utf-8"))
    stubs = {int(p["id"]): p for p in json.loads(STUBS.read_text(encoding="utf-8"))["problems"]}

    if doc.get("schema") != "efa-ai-claim-overlay-v1":
        errors.append("schema must be efa-ai-claim-overlay-v1")

    src = doc.get("source") or {}
    for field in ("name", "url", "retrieved", "page_sha256"):
        if not src.get(field):
            errors.append(f"source.{field} is required — an unsourced claim feed is a rumour")

    seen = set()
    for e in doc.get("entries", []):
        pid = e.get("erdos_id")
        where = f"entry #{pid}"
        if not isinstance(pid, int):
            errors.append(f"{where}: erdos_id must be an integer")
            continue
        if pid in seen:
            errors.append(f"{where}: duplicate entry")
        seen.add(pid)

        if pid not in stubs:
            errors.append(f"{where}: not present in atlas/stubs.json — the overlay may only "
                          f"annotate problems the hub actually indexes")
            continue

        if "claimed_system" in e or "claimed_verification" in e:
            errors.append(
                f"{where}: carries claimed_system/claimed_verification. Those fields were "
                f"mis-extracted from an adjacent card and are not recoverable per-record; "
                f"use registry_verification, taken from the record's own details.")

        if "registry_says_not_a_resolution" not in e:
            errors.append(
                f"{where}: registry_says_not_a_resolution is required. Whether the SOURCE "
                f"itself calls a claim a variant is the field that distinguishes a resolution "
                f"from a partial result, and omitting it makes every claim look alike.")

        if e.get("registry_says_not_a_resolution") and not e.get("registry_scope_note"):
            errors.append(
                f"{where}: flagged as not-a-resolution but quotes no scope note; the "
                f"source's own words are the evidence for that flag")

        if not e.get("claim_sources"):
            errors.append(f"{where}: no claim_sources — a claim we cannot point at is not "
                          f"recordable")

        verdict = e.get("our_verdict")
        if verdict not in ALLOWED_VERDICTS:
            errors.append(f"{where}: our_verdict {verdict!r} not in {sorted(ALLOWED_VERDICTS)}")

        # THE RULE.
        if e.get("status_changed_by_this_claim") is not False:
            errors.append(
                f"{where}: status_changed_by_this_claim must be false. A claim is not a "
                f"resolution; statuses follow the upstream record.")

        if e.get("upstream_finite_handle") != stubs[pid].get("upstream_finite_handle"):
            errors.append(
                f"{where}: upstream_finite_handle disagrees with the hub "
                f"({e.get('upstream_finite_handle')!r} vs "
                f"{stubs[pid].get('upstream_finite_handle')!r}). A claim against a problem "
                f"upstream calls decidable/falsifiable/verifiable must say so.")

        recorded = e.get("our_recorded_status")
        actual = stubs[pid].get("status")
        if recorded != actual:
            errors.append(
                f"{where}: our_recorded_status {recorded!r} disagrees with atlas/stubs.json "
                f"({actual!r}) — the overlay has drifted from the hub it annotates")

        # A verdict stronger than "not checked" must be backed by a certificate.
        if verdict in {"verified", "refuted", "convention-dependent"} and not e.get("our_certificate"):
            errors.append(
                f"{where}: our_verdict is {verdict!r} but no our_certificate path is given. "
                f"We do not assert an independent verdict without a replayable artifact.")

    counts = doc.get("counts") or {}
    hot = [e for e in doc.get("entries", [])
           if e.get("our_recorded_status") in ("open", "wall")]
    if counts.get("claims_against_problems_we_record_open_or_wall") != len(hot):
        errors.append(
            f"counts.claims_against_problems_we_record_open_or_wall says "
            f"{counts.get('claims_against_problems_we_record_open_or_wall')}, recomputed {len(hot)}")
    if counts.get("erdos_linked_claims") != len(doc.get("entries", [])):
        errors.append("counts.erdos_linked_claims disagrees with the entry list")

    if errors:
        print("ai-claim overlay FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"ai-claim overlay OK: {len(doc['entries'])} claims recorded, "
          f"{len(hot)} against problems we still record open/wall; "
          f"0 statuses changed by a claim")
    return 0


if __name__ == "__main__":
    sys.exit(main())
