#!/usr/bin/env python3
"""Validate atlas/openai_math.json, the index of external OpenAI manuscripts
tied to Erdős problems. Same rule as ai_claims: an external result never sets
a status. Exit 0 iff well formed, pinned to a commit, every entry sourced, every
cited Erdős id exists in the hub, and no entry claims to have moved a status."""
import json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
doc = json.loads((ROOT / "atlas" / "openai_math.json").read_text(encoding="utf-8"))
hub = {int(p["id"]) for p in json.loads((ROOT / "atlas" / "stubs.json").read_text(encoding="utf-8"))["problems"]}
err = []
if doc.get("schema") != "efa-external-corpus-v1": err.append("bad schema")
sha = doc.get("source", {}).get("commit", "")
if not re.fullmatch(r"[0-9a-f]{40}", sha): err.append("source commit not pinned")
for e in doc.get("entries", []):
    f = e.get("family")
    if e.get("status_changed_by_this_entry") is not False: err.append(f"{f}: status moved")
    if e.get("our_verdict") != "not independently checked" and not e.get("certificate"):
        err.append(f"{f}: verdict without certificate")
    if not e.get("manuscripts"): err.append(f"{f}: unsourced")
    for u in e["manuscripts"] + ([e["lean_scope_doc"]] if e.get("lean_scope_doc") else []):
        if f"/blob/{sha}/" not in u: err.append(f"{f}: link not pinned: {u}")
    for l in e.get("erdosproblems_links", []):
        if l["erdos_id"] not in hub: err.append(f"{f}: #{l['erdos_id']} not in hub")
    if re.search(r"(?i)\bbreakthrough\b", json.dumps(e, ensure_ascii=False)): err.append(f"{f}: hype word")
if doc.get("counts", {}).get("families") != len(doc.get("entries", [])): err.append("counts stale")
print("\n".join(err) or f"openai_math.json OK ({len(doc['entries'])} entries)")
sys.exit(1 if err else 0)
