#!/usr/bin/env python3
"""Validate atlas/tools.json (AI-assisted discovery tools, systems, registries,
datasets, benchmarks) and atlas/ai_results.json (quantitative results that
sources report or claim with AI assistance) against their schemas.

Beyond the schema: ids are unique, counts match, every URL is https, every
atlas node path that names a file exists, every erdos:<n> node is in the hub,
and our own wording avoids status-implying or hype words. URLs are skipped by
the word check because they are not our wording."""
import collections, json, pathlib, re, sys
from jsonschema import Draft202012Validator
ROOT = pathlib.Path(__file__).resolve().parent.parent
BANNED = re.compile(r"(?i)\b(solved|proven|breakthrough|records?)\b")
hub = {int(p["id"]) for p in json.loads((ROOT / "atlas" / "stubs.json").read_text(encoding="utf-8"))["problems"]}

def strings(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items(): yield from strings(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x): yield from strings(v, f"{path}[{i}]")
    elif isinstance(x, str): yield path, x

def check(name, schema_name, list_key, node_key, count_check):
    err = []
    doc = json.loads((ROOT / "atlas" / name).read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "atlas" / schema_name).read_text(encoding="utf-8"))
    for e in Draft202012Validator(schema).iter_errors(doc):
        err.append(f"{name}: schema: {'/'.join(map(str, e.path))}: {e.message}")
    if err: return err, doc
    items = doc[list_key]
    ids = [x["id"] for x in items]
    for i, n in collections.Counter(ids).items():
        if n > 1: err.append(f"{name}: duplicate id {i}")
    err += [f"{name}: {m}" for m in count_check(doc)]
    for x in items:
        for node in x[node_key]:
            m = re.fullmatch(r"erdos:(\d+)", node)
            if m:
                if int(m.group(1)) not in hub: err.append(f"{name}: {x['id']}: {node} not in hub")
            elif not (ROOT / node.split("#")[0]).exists():
                err.append(f"{name}: {x['id']}: node path missing: {node}")
    for path, s in strings(doc):
        if re.fullmatch(r"https://\S+", s): continue
        m = BANNED.search(s)
        if m: err.append(f"{name}: banned word '{m.group(0)}' at {path}")
    return err, doc

def tools_counts(d):
    c = d["counts"]; out = []
    if c["items"] != len(d["items"]): out.append("counts.items stale")
    if c["by_kind"] != dict(sorted(collections.Counter(x["kind"] for x in d["items"]).items())): out.append("counts.by_kind stale")
    return out

def results_counts(d):
    c = d["counts"]; E = d["entries"]; out = []
    if c["entries"] != len(E): out.append("counts.entries stale")
    for s in ("confirmed", "unconfirmed"):
        if c[f"ai_involvement_{s}"] != sum(e["ai_involvement"]["status"] == s for e in E): out.append(f"counts.ai_involvement_{s} stale")
    if c.get("unvetted", 0) != sum(e.get("vetting") == "unvetted" for e in E): out.append("counts.unvetted stale")
    for e in E:
        if e.get("vetting") == "unvetted" and e["attribution"] != "claimed": out.append(f"{e['id']}: unvetted entries must be attributed 'claimed'")
    return out

def main():
    e1, t = check("tools.json", "tools.schema.json", "items", "atlas_nodes_touched", tools_counts)
    e2, r = check("ai_results.json", "ai_results.schema.json", "entries", "atlas_nodes", results_counts)
    err = e1 + e2
    print("\n".join(err) or f"tools.json OK ({len(t['items'])} items); ai_results.json OK ({len(r['entries'])} entries)")
    return 1 if err else 0

if __name__ == "__main__":
    sys.exit(main())
