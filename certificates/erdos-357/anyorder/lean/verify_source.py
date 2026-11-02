#!/usr/bin/env python3
"""Audit the target header, source restrictions, pins, and line counts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
PIN = "0df444a360eaa60ab8c11dca51a86af692955474"
TOOLCHAIN = "leanprover/lean4:v4.33.1"
THEOREM = "erdos357_any_order_improvement"


def header(text: str) -> str:
    start = text.index("theorem " + THEOREM)
    return text[start:text.index(" := by", start)]


def main() -> None:
    challenge = (ROOT / "Challenge.lean").read_text()
    solution = (ROOT / "Solution.lean").read_text()
    assert header(challenge) == header(solution), "Target statements differ"
    assert len(re.findall(r"\bsorry\b", challenge)) == 1
    assert (ROOT / "lean-toolchain").read_text().strip() == TOOLCHAIN
    manifest = json.loads((ROOT / "lake-manifest.json").read_text())
    mathlib = next(p for p in manifest["packages"] if p["name"] == "mathlib")
    assert mathlib["rev"] == PIN
    assert f'rev = "{PIN}"' in (ROOT / "lakefile.toml").read_text()
    sources = sorted(ROOT.glob("*.lean")) + sorted((ROOT / "Erdos357").glob("*.lean"))
    counts = {}
    hashes = {}
    forbidden = re.compile(r"\b(sorry|admit|axiom|native_decide|unsafe|implemented_by)\b")
    for path in sources:
        text = path.read_text()
        name = path.relative_to(ROOT).as_posix()
        counts[name] = len(text.splitlines())
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        if path.name != "Challenge.lean":
            assert not forbidden.search(text), f"Forbidden proof escape in {name}"
            assert not re.search(r"^import\s+.*\bChallenge\b", text, re.M)
    for name in ["lean-toolchain", "lakefile.toml", "lake-manifest.json"]:
        hashes[name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    print(json.dumps({
        "target_headers_identical": True,
        "only_challenge_contains_sorry": True,
        "toolchain": TOOLCHAIN,
        "mathlib_commit": PIN,
        "line_counts": counts,
        "proof_lines_excluding_challenge_and_audit": sum(
            n for name, n in counts.items() if name not in ["Challenge.lean", "AxiomAudit.lean"]),
        "total_lean_lines": sum(counts.values()),
        "sha256": hashes,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
