#!/usr/bin/env python3
"""Re-extract bibliographic metadata from the hash-pinned OpenAI manuscript map.

No network access, proof execution, or canonical-status updates. Source files
stay outside this repository. Existing outputs are checked, never overwritten.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def extract(text):
    headers = list(re.finditer(r"^\*\*(\d{3})\. (.*?)\*\*(.*)$", text, re.M))
    families = []
    for i, header in enumerate(headers):
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body = text[header.end():end]
        lean = re.search(r"\[Lean\]\((lean/docs/\d{3}\.md)\)", header[3])
        papers = re.findall(r"&emsp;\[(.*?)\]\((preprints/[^)]+)\)", body)
        if not papers:
            raise ValueError(f"No manuscripts in family {header[1]}")
        families.append({
            "family_id": header[1],
            "title": html.unescape(re.sub(r"<[^>]+>", "", header[2])).rstrip("."),
            "lean_scope_path": lean[1] if lean else None,
            "manuscripts": [{"title": html.unescape(re.sub(r"<[^>]+>", "", title)),
                             "path": path} for title, path in papers],
        })
    ids = [f["family_id"] for f in families]
    paths = [p["path"] for f in families for p in f["manuscripts"]]
    counts = {"families": len(families), "manuscripts": len(paths),
              "families_with_catalogue_lean_link": sum(
                  f["lean_scope_path"] is not None for f in families)}
    if counts != {"families": 372, "manuscripts": 722,
                  "families_with_catalogue_lean_link": 235}:
        raise ValueError(f"Unexpected release counts: {counts}")
    if len(set(ids)) != len(ids) or len(set(paths)) != len(paths):
        raise ValueError("Duplicate family or manuscript")
    return counts, families


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True,
                        help="External directory containing pinned CONTENTS.md")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sources = json.loads((HERE / "sources.json").read_text())
    source = next(s for s in sources["files"] if s["path"] == "CONTENTS.md"
                  and s["repository"] == "openai/math")
    raw = (args.source_dir / "CONTENTS.md").read_bytes()
    if hashlib.sha256(raw).hexdigest() != source["sha256"]:
        raise ValueError("CONTENTS.md does not match the recorded SHA-256")
    counts, families = extract(raw.decode("utf-8"))
    result = {
        "schema": "efa-openai-math-catalogue-v1",
        "release_date": "2026-10-06",
        "repository": "https://github.com/openai/math",
        "commit": source["commit"],
        "source_sha256": source["sha256"],
        "attribution": "Bibliographic metadata from OpenAI, Apache-2.0; see sources.json.",
        "scope": "External catalogue metadata only. Family IDs are NOT Erdos problem IDs. "
                 "A Lean link does not establish coverage of every manuscript, successful "
                 "local verification, peer review, or canonical problem status.",
        "local_proof_verification": "NOT_RUN",
        "canonical_status_changes": False,
        "counts": counts,
        "families": families,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    output = HERE / "catalogue.json"
    if args.check:
        if output.read_text() != rendered:
            raise ValueError("catalogue.json differs from pinned source extraction")
        print(f"PASS: pinned catalogue matches; {counts}; no proofs checked")
    else:
        with output.open("x") as stream:
            stream.write(rendered)
        print(f"Created {output}")


if __name__ == "__main__":
    main()
