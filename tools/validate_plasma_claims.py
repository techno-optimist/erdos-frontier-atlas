#!/usr/bin/env python3
"""Validate atlas/plasma_claims.json, the Plasma AI (erdosproblems.ai wiki)
claim overlay. Same rule as ai_claims and openai_math: an external standing
never sets a status. Exit 0 iff well formed, pinned to a commit, CC BY 4.0
attributed per record, every id in the hub with a matching status copy, and no
entry claims to have moved a status."""
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
doc = json.loads((ROOT / "atlas" / "plasma_claims.json").read_text(encoding="utf-8"))
hub = {int(p["id"]): p for p in json.loads((ROOT / "atlas" / "stubs.json").read_text(encoding="utf-8"))["problems"]}
ATTR = "Plasma AI, github.com/plasma-ai/erdos, CC BY 4.0"
REVIEWS = {"source-checked", "annotated", "not-accepted", "flagged"}
err = []
if doc.get("schema") != "efa-plasma-claim-overlay-v1": err.append("bad schema")
sha = doc.get("source", {}).get("commit", "")
if not re.fullmatch(r"[0-9a-f]{40}", sha): err.append("source commit not pinned")
if doc.get("source", {}).get("attribution") != ATTR: err.append("source attribution missing")
seen = set()
for e in doc.get("entries", []):
    n = e.get("erdos_id")
    key = (n, e.get("bucket"))
    if key in seen: err.append(f"#{n}: duplicate in bucket")
    seen.add(key)
    if n not in hub: err.append(f"#{n}: not in hub"); continue
    if e.get("status_changed_by_this_entry") is not False: err.append(f"#{n}: status moved")
    if e.get("our_recorded_status") != hub[n]["status"]: err.append(f"#{n}: status copy stale")
    src = e.get("source", {})
    if src.get("license") != "CC-BY-4.0" or src.get("attribution") != ATTR or src.get("commit") != sha:
        err.append(f"#{n}: per-record CC BY 4.0 source missing or unpinned")
    if e.get("atlas_review") not in REVIEWS: err.append(f"#{n}: bad review verdict")
    for c in e.get("claims", []):
        if f"/blob/{sha}/" not in c.get("url", ""): err.append(f"#{n}: claim url not pinned")
        if set(c) - {"file", "plasma_claim_status", "claim", "scope", "published", "authors", "links", "url"}:
            err.append(f"#{n}: claim row carries non-metadata fields")
    if "statement" in e or "desc" in e: err.append(f"#{n}: carries prose")
    if re.search(r"(?i)\bbreakthrough\b|A364153", json.dumps(e, ensure_ascii=False)): err.append(f"#{n}: banned term")
if doc.get("counts", {}).get("entries") != len(doc.get("entries", [])): err.append("counts stale")
print("\n".join(err) or f"plasma_claims.json OK ({len(doc['entries'])} entries)")
sys.exit(1 if err else 0)
