#!/usr/bin/env python3
"""Fail-closed integrity checks for the published Atlas snapshot and views."""

import json
import hashlib
import sys
import subprocess
import re
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "atlas" / "problems.json"


def fail(message: str) -> None:
    raise SystemExit(f"atlas integrity error: {message}")


def main() -> None:
    document = json.loads(ATLAS.read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "atlas" / "schema.json").read_text(encoding="utf-8"))
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
    if document.get("atlas_version") != "0.2.0" or document.get("generated") != "2026-07-13":
        fail("Atlas release identity changed")

    by_id = {entry["id"]: entry for entry in problems}
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    schema_errors = [
        f"{entry['id']}: {error.message}"
        for entry in problems
        for error in validator.iter_errors(entry)
    ]
    if schema_errors:
        fail(f"entry schema validation failed: {schema_errors[0]}")
    if by_id[1].get("p42_slug") != "distinct-subset-sums-a11":
        fail("Erdos #1 must target the open a(11) board")
    if "130,000" not in json.dumps(by_id[67], ensure_ascii=False):
        fail("Erdos #67 lost the exactly re-verified 130,000 frontier")
    if by_id[21].get("lane") != "exact-backtracking":
        fail("q(6) must route to orderly generation/exact backtracking")
    q6 = json.dumps(by_id[21], ensure_ascii=False).lower()
    if "14 ≤ f(6) ≤ 18" not in by_id[21].get("statement", ""):
        fail("q(6) statement lost the current 14..18 bracket")
    if "orderly generation" not in by_id[21].get("attack", "").lower():
        fail("q(6) attack lost the orderly-generation route")
    if "per-m sat + cegar + drat" in q6 or "q(6) ∈ [13,18]" in by_id[21].get("verdict", ""):
        fail("q(6) entry contains a stale bracket or obsolete SAT route")
    if by_id[86].get("p42_slug") != "hypercube-q7-c4-free":
        fail("C4-free Q7 must link to its packaged finite-frontier board")
    if by_id[20].get("board_class") == "READY":
        fail("sunflower entry must be split into one finite frontier per board")
    if by_id[52].get("board_class") == "READY":
        fail("sum-product requires a concrete seeded finite frontier")
    if "minimum degree" not in by_id[552].get("board_class_reason", ""):
        fail("C4-vs-star routing must use the complementary degree condition")
    erdos_552 = by_id[552]
    if "a(12..16)" not in erdos_552.get("frontier", ""):
        fail("C4-vs-star certified frontier is stale")
    # Source-freshness correction 2026-07-16: a(17)=22 has been closed since
    # Parsons 1975 (independently: certified lower witness + ex(22;C4)=52
    # counting). The board must never again present that cell as open.
    if "a(17) = 22 CLOSED" not in erdos_552.get("frontier", ""):
        fail("C4-vs-star frontier must record a(17)=22 CLOSED (Parsons 1975)")
    if "next open term 22" in erdos_552.get("frontier", ""):
        fail("C4-vs-star frontier regressed to the stale open-a(17) claim")
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
    replay = subprocess.run(
        [sys.executable, str(ROOT / evidence["verifier_path"])],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if replay.returncode != 0:
        fail(f"C4-vs-star certificate replay failed: {replay.stderr.strip()}")
    try:
        replay_report = json.loads(replay.stdout)
    except json.JSONDecodeError as exc:
        fail(f"C4-vs-star verifier emitted invalid JSON: {exc}")
    if replay_report.get("valid") is not True or len(replay_report.get("results", [])) != 5:
        fail("C4-vs-star certificate replay did not certify all five exact terms")
    lower_bounds = replay_report.get("lower_bounds", [])
    if len(lower_bounds) != 1 or lower_bounds[0].get("n") != 17 or lower_bounds[0].get("value") != 22:
        fail("C4-vs-star certificate replay did not certify the n=17 lower bound")
    artifact_sha256 = evidence.get("artifact_sha256")
    if replay_report.get("certificate_sha256") != artifact_sha256:
        fail("C4-vs-star replay is not bound to the declared artifact digest")
    if evidence.get("digest") != f"sha256:{artifact_sha256}":
        fail("C4-vs-star evidence digest is not bound to artifact_sha256")
    expected_claims = [
        f"R(C4,K1,{result['n']})={result['value']}"
        for result in replay_report["results"]
    ] + ["R(C4,K1,17)>=22"]
    if evidence.get("claims") != expected_claims:
        fail("C4-vs-star evidence claims do not match the certificate replay")
    expected_frontier = "Repository-certified: a(12..16) = 17,18,19,20,21. a(17) = 22 CLOSED (Parsons 1975: R(C4,K1,q^2+1)=q^2+q+2 at q=4; independently, the certified 21-vertex witness gives a(17)>=22 and min-degree-5 on 22 vertices needs 55 edges > ex(22;C4)=52 [OEIS A006855], so a(17)<=22). CORRECTION 2026-07-17: the earlier 'a(39)=46 NEW VALUE' claim is RETRACTED \u2014 DS1 rev.18 (Apr 2026) Table IVa lists a(39)='46-47' OPEN (lower 46 = Wu-Sun-Radziszowski 2015 Cons.5; upper 47 = Dybizbanski-Dzido); Boza arXiv:2409.12770's '/46' cell is an off-by-one wheel-convention error vs its own source. Our 45-vertex witness (certificates/erdos-552-f39/) re-derives the 2015 lower bound. Open deciders: a(39) via SAT cell (46-vtx min-deg-7: UNSAT=>46, SAT=>47); a(42) via (49,7); a(44) via (51,7). Consult DS1, not single-survey tables."
    if erdos_552.get("frontier") != expected_frontier:
        fail("C4-vs-star frontier does not match the certificate replay")
    expected_current_record = "Exact values known in the literature for all n <= 38 (Boza arXiv:2409.12770 table with references; e.g. f(12..17)=17..22 published 1975-2018 \u2014 OEIS A006672's b-file, stopping at n=11, is far behind the survey literature). P42 certificates for a(12..16) and the a(17) lower witness are independent machine-checkable re-derivations, not novel records."
    if erdos_552.get("current_record") != expected_current_record:
        fail("C4-vs-star current record does not match the certificate replay")
    expected_coverage = [
        {
            "axis": "n", "start": 12, "end": 16, "status": "CERTIFIED",
            "result": "Exact values 17,18,19,20,21",
            "artifact_sha256": artifact_sha256,
        },
        {
            "axis": "m", "start": 21, "end": 21, "status": "CERTIFIED",
            "result": "21-vertex witness proves R(C4,K1,17) >= 22",
            "artifact_sha256": artifact_sha256,
            "where": {"n": 17},
        },
        {
            "axis": "m", "start": 22, "end": 22, "status": "EXCLUDED",
            "result": "Cell closed by literature, not by this compute: min-degree-5 on 22 vertices needs 55 edges > ex(22;C4)=52 [OEIS A006855], so no witness exists; a(17)=22 (Parsons 1975)",
            "where": {"n": 17},
        },
    ]
    if erdos_552.get("compute", {}).get("coverage") != expected_coverage:
        fail("C4-vs-star compute coverage does not match the certificate replay")

    for entry in problems:
        for field in ("title", "finite_object"):
            value = entry.get(field, "")
            if "&lt;" in value or "&gt;" in value:
                fail(f"HTML entity leaked into display field {entry['id']}:{field}")

    catalog = (ROOT / "views" / "board_catalog.md").read_text(encoding="utf-8")
    lanes = (ROOT / "atlas" / "lanes.md").read_text(encoding="utf-8")
    section_pattern = re.compile(
        r"^## BOARD-(READY|HEAVY) \((\d+)\).*?$(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    catalog_sections = {}
    for label, declared_count, body in section_pattern.findall(catalog):
        ids_in_view = [int(value) for value in re.findall(r"^\| \[(\d+)\]\(", body, re.MULTILINE)]
        if int(declared_count) != len(ids_in_view):
            fail(f"board catalog {label} heading count does not match its rows")
        if len(ids_in_view) != len(set(ids_in_view)):
            fail(f"board catalog {label} contains duplicate problem rows")
        catalog_sections[label] = set(ids_in_view)
    expected_catalog_sections = {
        label: {entry["id"] for entry in problems if entry["board_class"] == label}
        for label in ("READY", "HEAVY")
    }
    if catalog_sections != expected_catalog_sections:
        fail(
            "board catalog membership differs from atlas/problems.json: "
            f"expected {expected_catalog_sections!r}, received {catalog_sections!r}"
        )
    if "≈13,000–14,000" in catalog or "past ~14,000" in lanes:
        fail("generated views contain the obsolete EDP frontier")
    if "| SAT+DRAT-nonexistence | MOVABLE | `q6-intersecting-hypergraph`" in catalog:
        fail("board catalog contains the obsolete q(6) SAT route")
    if "a(17) ∈ [22,23]" not in catalog:
        fail("board catalog lost the certified C4-star n=17 frontier")

    linked_packages = sum(entry.get("p42_slug") is not None for entry in problems)
    if linked_packages != 7:
        fail("linked P42 package count changed")
    zenodo = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
    zenodo_description = zenodo.get("description", "")
    required_release_facts = (
        "13 BOARD-READY", "14 BOARD-HEAVY", "24 named walls",
        "seven boards", "22 &lt;= R(C4,K1,17) &lt;= 23",
    )
    if not all(fact in zenodo_description for fact in required_release_facts):
        fail("Zenodo release metadata contains stale board counts")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    top_level = dict(re.findall(r'^([a-z][a-z-]*):\s*"?([^"\n]+)"?\s*$', citation, re.MULTILINE))
    required_citation_facts = (
        "13 BOARD-READY", "14 BOARD-HEAVY", "24 named walls",
        "seven Atlas", "22 <= R(C4,K1,17) <= 23",
    )
    if (
        top_level.get("version") != document["atlas_version"]
        or top_level.get("date-released") != document["generated"]
        or not all(fact in citation for fact in required_citation_facts)
    ):
        fail("citation metadata is stale")

    print("atlas integrity: 51 entries, counts and routing invariants verified")


if __name__ == "__main__":
    main()
