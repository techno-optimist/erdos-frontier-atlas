#!/usr/bin/env python3
"""build_plasma_claims.py: compile atlas/plasma_claims.json from a checkout of
github.com/plasma-ai/erdos (wiki content CC BY 4.0).

A claim feed, not a status source (CLAUDE.md rule 1). It records where Plasma
AI's wiki standing differs from this atlas, the claim pages Plasma cites, and
the atlas's own review of each difference. It copies METADATA ONLY: standing
labels, claim status/scope/date/authors, links and bound values. It never copies
problem statements, claim descriptions or any erdosproblems.com prose.

Usage: python3 tools/build_plasma_claims.py --plasma ../plasma-erdos
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "atlas" / "plasma_claims.json"
REPO = "plasma-ai/erdos"
LICENSE = "CC-BY-4.0"
ATTRIBUTION = "Plasma AI, github.com/plasma-ai/erdos, CC BY 4.0"

# Bucket 1: Plasma's wiki marks these solved; the atlas records them open (or wall).
SOLVED_VS_OPEN = [3, 14, 96, 108, 111, 131, 138, 173, 174, 184, 196, 252, 254, 256,
                  304, 341, 371, 374, 408, 424, 431, 520, 521, 551, 579, 653, 791, 802,
                  809, 859, 928, 944, 952, 968, 978, 993, 1002, 1057, 1062, 1112, 1150,
                  1155, 1220]
# Bucket 2: Plasma's wiki marks these open; the atlas records them solved-upstream.
OPEN_VS_SOLVED = [736, 739, 910, 1154, 1169, 1171, 1174, 1176]
# Bucket 4: Plasma's own 2026-10-19 bound claims.
BOUND_CLAIMS = {
    962: {"claim_file": "2026_10_19_plasma_ai.md",
          "bound": "k(n) < max(64, (2^15 n)^(11/28)) for every n; k(n) <<_eps n^(38/97+eps) using Bourgain's exponent pair",
          "previous_published_exponent": "2/5"},
    699: {"claim_file": "2026_10_19_plasma_ai.md",
          "bound": "a common prime p >= i dividing C(n,i) and C(n,j) for every triple with i = 7 or i >= 9; at i = 3 no exceptional triple with n <= 10^19, v_2(n) <= 48, or at most two primes dividing (n-2)/2",
          "depends_on": "van Doorn and Rocca manuscripts (unreviewed, per Plasma)"},
}

HELD = ("Atlas status held: upstream (teorth/erdosproblems, Bloom) still labels this "
        "problem open, and a claim never sets a status here (CLAUDE.md rule 1).")

# Atlas review of bucket 1. Default verdict: annotated (Plasma's label recorded as
# 'solved (unverified by atlas)'; cited source link resolves; content not re-verified).
REVIEW_1 = {
    802: {"verdict": "source-checked",
          "note": "Plasma's standing rests on OpenAI's release (github.com/openai/math, family 184). "
                  "The atlas replayed that Lean proof and kernel-checked it (standard axioms only; "
                  "statement reviewed as faithful to the d >= 2 form); see atlas/openai_math.json "
                  "family 184 and receipt projectforty2.ai/data/ford_receipts/oai184_lean_check.txt. "
                  "Credit: OpenAI. " + HELD},
    131: {"verdict": "source-checked",
          "note": "Displayed growth question answered in the negative by Pham and Zakharov "
                  "(GAFA 2025, doi 10.1007/s00039-025-00728-8; arXiv 2410.14624, abstract checked: "
                  "largest such subset of [n] has size n^(1/4+o(1))). Only that question is marked "
                  "answered; the atlas's computed values (T9=107, T10=155) are unchanged. A sharper "
                  "N^(1/5+o(1)) statement circulating on Plasma's page is an unreviewed claim and is "
                  "not adopted. " + HELD},
    138: {"verdict": "not-accepted",
          "note": "Plasma marks this solved because accepted partial results settle part of the "
                  "question and it reads the bound-improvement request as non-blocking; Plasma's own "
                  "page records the quotient question W(k+1)/W(k) -> infinity as still open. The "
                  "atlas's per-branch wall is unaffected."},
    3: {"verdict": "annotated",
        "note": "Caveat: the curator's 8 Oct 2026 post, cited on Plasma's page, says the released "
                "Lean appears to prove only a weaker bound; Plasma reads that weaker bound as still "
                "giving the yes answer. Not re-verified by the atlas. " + HELD},
    111: {"verdict": "annotated", "note": "Self-claim by Plasma AI; not independently checked. " + HELD},
    173: {"verdict": "annotated", "note": "Self-claim by Plasma AI; not independently checked. " + HELD},
    408: {"verdict": "annotated", "note": "Self-claim by Plasma AI; not independently checked. " + HELD},
    424: {"verdict": "annotated", "note": "Cited proof is a Google Drive document; not checkable as a pinned source. " + HELD},
    256: {"verdict": "annotated", "note": "Plasma reads a refereed bound (Belov and Konyagin 1996) as answering the displayed question; upstream has not adopted that reading. " + HELD},
    791: {"verdict": "annotated", "note": "Plasma reads refereed bounds (Yu 2015, Kohonen 2017) as answering the displayed guess; upstream has not adopted that reading. " + HELD},
    1220: {"verdict": "annotated", "note": "Plasma combines refereed results (Erdős, Hajnal and Rado 1965; Shelah and Stanley 1987) into an independence standing; upstream has not adopted it. " + HELD},
    993: {"verdict": "annotated", "note": "Listed for completeness only. " + HELD},
}

REVIEW_2_COMMON = (
    "Upstream's label is a one-sided consistency result ('{raw}'). When this overlay was first "
    "built, tools/build_stubs.py mapped every non-open upstream state to solved-upstream; since "
    "PR #190 the atlas records this label as one-sided-upstream, so the status copy here follows "
    "it. Plasma reads the problem as 'open'. Kept as flagged: whether one-sided-upstream and "
    "Plasma's 'open' should be reconciled is a separate decision.")
REVIEW_2 = {
    910: "Upstream's label is 'disproved', resting on Rudin's counterexamples under the continuum "
         "hypothesis; Plasma argues the cited paper does not establish the first question's step and "
         "that the second question's wording is defective. The atlas mirrors upstream faithfully, but "
         "solved-upstream for a CH-conditional result is disputed. Flagged, not changed.",
}


def git_sha(repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def frontmatter(path: Path) -> dict:
    m = re.match(r"---\n(.*?)\n---", path.read_text(encoding="utf-8"), re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def problem_dir(plasma: Path, n: int) -> Path:
    hits = list((plasma / "wiki" / "problems").glob(f"*/E{n:04d}"))
    if len(hits) != 1:
        raise SystemExit(f"#{n}: expected one Plasma problem dir, got {hits}")
    return hits[0]


def claim_rows(plasma: Path, d: Path, sha: str, only=None):
    rows = []
    for cp in sorted((d / "claims").glob("*.md")):
        if cp.name == "_index.md" or (only and cp.name != only):
            continue
        fm = frontmatter(cp)
        rows.append({
            "file": str(cp.relative_to(plasma)),
            "plasma_claim_status": fm.get("status"),
            "claim": fm.get("claim"),
            "scope": fm.get("scope"),
            "published": str(fm.get("published")) if fm.get("published") else None,
            "authors": fm.get("authors") or [],
            "links": [l["url"] for l in (fm.get("links") or []) if isinstance(l, dict) and l.get("url")],
            "url": f"https://github.com/{REPO}/blob/{sha}/{cp.relative_to(plasma)}",
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plasma", required=True, type=Path)
    a = ap.parse_args()
    plasma = a.plasma.resolve()
    sha = git_sha(plasma)
    hub = {p["id"]: p for p in json.loads((ROOT / "atlas" / "stubs.json").read_text())["problems"]}

    def base(n, bucket, plasma_status_override=None):
        d = problem_dir(plasma, n)
        fm = frontmatter(d / "_index.md")
        h = hub[n]
        return d, {
            "erdos_id": n,
            "bucket": bucket,
            "plasma_wiki_status": fm.get("status"),
            "plasma_wiki_claim": fm.get("claim"),
            "plasma_status": plasma_status_override,
            "our_recorded_status": h["status"],
            "upstream_status": h["upstream_status"],
            "upstream_state_raw": h["upstream_state_raw"],
            "status_changed_by_this_entry": False,
            "source": {"repo": REPO, "file": str((d / "_index.md").relative_to(plasma)),
                       "commit": sha, "license": LICENSE, "attribution": ATTRIBUTION},
        }

    entries = []
    for n in SOLVED_VS_OPEN:
        d, e = base(n, "plasma-solved-vs-atlas-open", "solved (unverified by atlas)")
        r = REVIEW_1.get(n, {"verdict": "annotated",
                             "note": "Cited source link resolves (checked 2026-10-29); content not "
                                     "re-verified by the atlas. " + HELD})
        e["atlas_review"] = r["verdict"]
        e["atlas_review_note"] = r["note"]
        e["claims"] = [c for c in claim_rows(plasma, d, sha) if c["plasma_claim_status"] == "accepted"]
        entries.append(e)
    for n in OPEN_VS_SOLVED:
        d, e = base(n, "plasma-open-vs-atlas-solved-upstream", "open")
        e["atlas_review"] = "flagged"
        e["atlas_review_note"] = REVIEW_2.get(n, REVIEW_2_COMMON.format(raw=e["upstream_state_raw"]))
        e["claims"] = claim_rows(plasma, d, sha)
        entries.append(e)
    for n in CLAIMED_VS_OPEN:
        d, e = base(n, "plasma-claimed-vs-atlas-open", "claimed (unverified by atlas)")
        e["atlas_review"] = "annotated"
        e["atlas_review_note"] = "Plasma lists an open claim not yet accepted. " + HELD
        e["claims"] = [c for c in claim_rows(plasma, d, sha) if c["plasma_claim_status"] == "claimed"]
        entries.append(e)
    for n, b in BOUND_CLAIMS.items():
        d, e = base(n, "plasma-bound-claim-2026-10-19", "claimed (unverified by atlas)")
        e["atlas_review"] = "annotated"
        e["atlas_review_note"] = "Plasma AI's own tier-0 claim, catalog acceptance pending; bound values kept as metadata only. " + HELD
        e["bound_claim"] = {k: v for k, v in b.items() if k != "claim_file"}
        e["claims"] = claim_rows(plasma, d, sha, only=b["claim_file"])
        entries.append(e)

    from collections import Counter
    doc = {
        "schema": "efa-plasma-claim-overlay-v1",
        "purpose": "A claim feed, not a status source. Records where Plasma AI's erdosproblems.ai wiki "
                   "(github.com/plasma-ai/erdos) differs from this atlas, the claim pages Plasma cites, "
                   "and the atlas's review of each difference. Adding an entry NEVER changes a "
                   "problem's status in this atlas: status changes when upstream changes or when the "
                   "atlas holds replayable evidence.",
        "source": {"repo": REPO, "url": f"https://github.com/{REPO}", "commit": sha,
                   "license": "CC-BY-4.0 (wiki content); Apache-2.0 (code)",
                   "attribution": ATTRIBUTION, "retrieved": "2026-10-29",
                   "changes": "Metadata only (standing labels, claim status, scope, dates, authors, links, bound "
                              "values), re-keyed per Erdős number and annotated with the atlas's own review. No "
                              "problem statements, claim descriptions or erdosproblems.com prose copied."},
        "review_legend": {
            "source-checked": "the cited source was opened and supports the stated standing; status still held per rule 1",
            "annotated": "Plasma's label kept as unverified by atlas; atlas status kept",
            "not-accepted": "the atlas does not accept Plasma's standing; reason in the note",
            "flagged": "Plasma's label disagrees with ours and ours may be the one at fault; not changed here"},
        "counts": {"entries": len(entries),
                   "by_bucket": dict(sorted(Counter(e["bucket"] for e in entries).items())),
                   "by_review": dict(sorted(Counter(e["atlas_review"] for e in entries).items()))},
        "entries": entries,
    }
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(doc["counts"], indent=1))


CLAIMED_VS_OPEN = [81, 117, 129, 143, 172, 176, 181, 242, 260, 267, 278, 279, 289, 301, 302, 306,
                   326, 327, 336, 348, 390, 394, 398, 415, 416, 456, 486, 488, 489, 506, 514, 522,
                   524, 536, 538, 550, 569, 593, 612, 620, 623, 638, 655, 662, 671, 689, 701, 710,
                   740, 742, 768, 769, 776, 786, 788, 789, 790, 796, 817, 821, 836, 848, 870, 876,
                   883, 906, 956, 971, 973, 983, 995, 996, 1016, 1033, 1038, 1039, 1040, 1041, 1054,
                   1059, 1061, 1070, 1075, 1083, 1110, 1117, 1122, 1133, 1139, 1144, 1151, 1152, 1177,
                   1182, 1183, 1188, 1189, 1199, 1201, 1207, 1212, 1221]

if __name__ == "__main__":
    main()
