#!/usr/bin/env python3
"""Fail-closed integrity checks for the published Atlas snapshot and views."""

import json
import hashlib
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "atlas" / "problems.json"


def fail(message: str) -> None:
    raise SystemExit(f"atlas integrity error: {message}")


def main() -> None:
    document = json.loads(ATLAS.read_text(encoding="utf-8"))
    problems = document.get("problems")
    if not isinstance(problems, list) or len(problems) != 51:
        fail("problems must contain exactly 51 entries")

    ids = [entry.get("id") for entry in problems]
    if len(set(ids)) != len(ids) or any(not isinstance(value, int) for value in ids):
        fail("problem ids must be unique integers")

    classes = Counter(entry.get("board_class") for entry in problems)
    expected = {"READY": 13, "HEAVY": 14, "NONE": 24}
    if dict(classes) != expected:
        fail(f"board classes changed: {dict(classes)!r}")
    if document.get("counts") != {"total": 51, **expected}:
        fail("declared counts do not match the release contract")

    by_id = {entry["id"]: entry for entry in problems}
    if by_id[1].get("p42_slug") != "distinct-subset-sums-a11":
        fail("Erdos #1 must target the open a(11) board")
    if "130,000" not in json.dumps(by_id[67], ensure_ascii=False):
        fail("Erdos #67 lost the exactly re-verified 130,000 frontier")
    if by_id[21].get("lane") != "exact-backtracking":
        fail("q(6) must route to orderly generation/exact backtracking")
    if by_id[20].get("board_class") == "READY":
        fail("sunflower entry must be split into one finite frontier per board")
    if by_id[52].get("board_class") == "READY":
        fail("sum-product requires a concrete seeded finite frontier")
    if "minimum degree" not in by_id[552].get("board_class_reason", ""):
        fail("C4-vs-star routing must use the complementary degree condition")
    erdos_552 = by_id[552]
    if "a(12..16)" not in erdos_552.get("frontier", ""):
        fail("C4-vs-star certified frontier is stale")
    evidence = erdos_552.get("evidence", {})
    for path_key, digest_key in (
        ("artifact_path", "artifact_sha256"),
        ("verifier_path", "verifier_sha256"),
    ):
        artifact = ROOT / evidence.get(path_key, "")
        if not artifact.is_file():
            fail(f"C4-vs-star evidence file is missing: {path_key}")
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if digest != evidence.get(digest_key):
            fail(f"C4-vs-star evidence digest mismatch: {digest_key}")

    for entry in problems:
        for field in ("title", "finite_object"):
            value = entry.get(field, "")
            if "&lt;" in value or "&gt;" in value:
                fail(f"HTML entity leaked into display field {entry['id']}:{field}")

    catalog = (ROOT / "views" / "board_catalog.md").read_text(encoding="utf-8")
    lanes = (ROOT / "atlas" / "lanes.md").read_text(encoding="utf-8")
    if "≈13,000–14,000" in catalog or "past ~14,000" in lanes:
        fail("generated views contain the obsolete EDP frontier")
    if "| SAT+DRAT-nonexistence | MOVABLE | `q6-intersecting-hypergraph`" in catalog:
        fail("board catalog contains the obsolete q(6) SAT route")

    print("atlas integrity: 51 entries, counts and routing invariants verified")


if __name__ == "__main__":
    main()
