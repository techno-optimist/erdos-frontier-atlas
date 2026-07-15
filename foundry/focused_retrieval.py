#!/usr/bin/env python3
"""Read-only IDF/phrase-focused retrieval for a selected math frontier."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
from pathlib import Path
from urllib.parse import quote

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
OBS = HOME / "cultural-soliton-observatory"
DEFAULT_PROBLEMS = ROOT / "atlas" / "problems.json"
DEFAULT_DBS = {
    "atlas": OBS / "data" / "atlas.db",
    "atlas2": OBS / "data" / "atlas2.db",
    "arena": OBS / "data" / "arena_atlas.db",
    "aiwiki": OBS / "runs" / "aiwiki_full_20260515" / "aiwiki_atlas.db",
}
STOP = {
    "the", "and", "for", "from", "with", "into", "that", "this", "under", "over", "via",
    "new", "large", "small", "system", "systems", "problem", "frontiermath", "search",
}
MAX_MARKDOWN_CHARS = 16_000
PRIMARY_KEYS = {
    "frontier_atlas": ("id", "title", "lane", "board_class", "verifier", "current_record", "campaign_finding", "focus_score", "focus_excerpt"),
}


def sha_file(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ro_conn(path: Path) -> sqlite3.Connection:
    return sqlite3.connect("file:" + quote(str(path.resolve())) + "?mode=ro", uri=True)


def columns(con: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in con.execute(f"PRAGMA table_info({table})")}


def query_features(query: str) -> list[tuple[str, float]]:
    words = [word for word in re.findall(r"[a-z0-9][a-z0-9_+-]{2,}", query.lower()) if word not in STOP]
    words = list(dict.fromkeys(words))[:14]
    features = [(word, 1.0) for word in words]
    raw_words = [word for word in re.findall(r"[a-z0-9][a-z0-9_+-]{2,}", query.lower()) if word not in STOP]
    for left, right in zip(raw_words, raw_words[1:]):
        if len(left) >= 5 and len(right) >= 5:
            phrase = left + " " + right
            if phrase not in {value for value, _ in features}:
                features.append((phrase, 2.5))
    return features[:20]


def focus_excerpt(record: dict, text_cols: list[str], weighted: list[tuple[str, str, float]], max_chars: int = 900) -> dict | None:
    candidates = []
    for col in text_cols:
        value = record.get(col)
        if not isinstance(value, str):
            continue
        lowered = value.lower()
        for feature, _, weight in weighted:
            at = lowered.find(feature)
            if at >= 0:
                candidates.append((weight, len(feature), col, feature, at, value))
    if not candidates:
        return None
    _, _, col, feature, at, value = max(candidates)
    start = max(0, at - max_chars // 3)
    end = min(len(value), start + max_chars)
    start = max(0, end - max_chars)
    excerpt = value[start:end]
    if start:
        excerpt = "…" + excerpt
    if end < len(value):
        excerpt += "…"
    return {"column": col, "feature": feature, "text": excerpt}


def focused_rows(path: Path, table: str, query: str, limit: int, preferred_cols: list[str]) -> list[dict]:
    if not path.exists():
        return []
    con = ro_conn(path)
    try:
        available = columns(con, table)
        text_cols = [col for col in preferred_cols if col in available]
        if not text_cols:
            return []
        select_cols = [col for col in ("id", *preferred_cols, "verification_status", "novelty_fast", "math_domain", "artifact_kind", "section", "words") if col in available]
        haystack = "lower(" + " || ' ' || ".join(f"coalesce({col}, '')" for col in text_cols) + ")"
        total = int(con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        weighted = []
        for feature, boost in query_features(query):
            pattern = "%" + feature + "%"
            count = int(con.execute(f"SELECT COUNT(*) FROM {table} WHERE {haystack} LIKE ?", (pattern,)).fetchone()[0])
            if count:
                weighted.append((feature, pattern, boost * (math.log((total + 1) / (count + 1)) + 1.0)))
        if not weighted:
            return []
        score_sql = " + ".join(f"CASE WHEN {haystack} LIKE ? THEN ? ELSE 0 END" for _ in weighted)
        where_sql = " OR ".join(f"{haystack} LIKE ?" for _ in weighted)
        params = []
        for _, pattern, weight in weighted:
            params.extend((pattern, weight))
        params.extend(pattern for _, pattern, _ in weighted)
        rows = con.execute(
            f"SELECT {', '.join(select_cols)}, ({score_sql}) AS focus_score FROM {table} WHERE {where_sql} ORDER BY focus_score DESC LIMIT ?",
            (*params, int(limit)),
        ).fetchall()
        out = []
        for row in rows:
            record = dict(zip([*select_cols, "focus_score"], row))
            text = " ".join(str(record.get(col, "")) for col in text_cols).lower()
            record["matched_features"] = [feature for feature, _, _ in weighted if feature in text]
            record["focus_score"] = round(float(record["focus_score"]), 4)
            record["focus_excerpt"] = focus_excerpt(record, text_cols, weighted)
            for col in text_cols:
                if isinstance(record.get(col), str):
                    record[col] = record[col][:300]
            out.append(record)
        return out
    finally:
        con.close()


def public_atlas_rows(path: Path, query: str, limit: int) -> list[dict]:
    document = json.loads(path.read_text())
    records = document.get("problems", [])
    features = query_features(query)
    weighted = []
    atlas_fields = ("id", "title", "lane", "verifier", "current_record", "campaign_finding", "beatable_reason", "attack", "wall_reason")
    haystacks = [" ".join(str(row.get(key, "")) for key in atlas_fields).lower() for row in records]
    for feature, boost in features:
        count = sum(feature in text for text in haystacks)
        if count:
            weighted.append((feature, boost * (math.log((len(records) + 1) / (count + 1)) + 1.0)))
    ranked = []
    for row, text in zip(records, haystacks):
        matched = [feature for feature, _ in weighted if feature in text]
        if not matched:
            continue
        score = sum(weight for feature, weight in weighted if feature in text)
        excerpt = focus_excerpt(row, ["title", "verifier", "current_record", "campaign_finding", "beatable_reason", "attack", "wall_reason"], [(feature, "%" + feature + "%", weight) for feature, weight in weighted])
        ranked.append({
            **{key: row.get(key) for key in ("id", "title", "lane", "board_class", "verifier", "current_record", "campaign_finding", "beatable_reason", "wall_reason") if row.get(key) is not None},
            "focus_score": round(score, 4), "matched_features": matched, "focus_excerpt": excerpt,
        })
    ranked.sort(key=lambda row: (-row["focus_score"], int(row["id"])))
    return ranked[:limit]


def retrieve(query: str, dbs: dict[str, Path], limit: int, problems_path: Path = DEFAULT_PROBLEMS) -> dict:
    before = {name: sha_file(path) for name, path in dbs.items()}
    problems_before = sha_file(problems_path)
    surfaces = {
        "frontier_atlas": public_atlas_rows(problems_path, query, limit),
        "atlas": focused_rows(dbs["atlas"], "thoughts", query, limit, ["text", "content", "anchor"]),
        "atlas2": focused_rows(dbs["atlas2"], "thoughts", query, max(3, limit // 2), ["text", "content", "anchor"]),
        "arena_problems": focused_rows(dbs["arena"], "problems", query, limit, ["title", "slug", "scoring"]),
        "arena_concepts": focused_rows(dbs["arena"], "concepts", query, limit, ["canonical_name", "description"]),
        "aiwiki": focused_rows(dbs["aiwiki"], "docs", query, limit, ["title", "text", "aiwiki", "record_key"]),
    }
    after = {name: sha_file(path) for name, path in dbs.items()}
    problems_after = sha_file(problems_path)
    return {
        "schema": "p42-foundry-focused-context-v1", "query": query,
        "features": [feature for feature, _ in query_features(query)], "surfaces": surfaces,
        "databases": {
            name: {
                "hash_before": before[name],
                "hash_after": after[name],
                "read_only_verified": bool(before[name]) and before[name] == after[name],
            }
            for name in dbs
        },
        "sources": {
            "frontier_atlas": {
                "hash_before": problems_before,
                "hash_after": problems_after,
                "read_only_verified": bool(problems_before) and problems_before == problems_after,
            }
        },
    }


def compact_row(surface: str, row: dict, rank: int) -> dict:
    """Give the worker one rich anchor per surface and terse alternatives."""
    if rank == 0:
        keys = PRIMARY_KEYS.get(surface, ("id", "title", "text", "content", "anchor", "canonical_name", "description", "verification_status", "math_domain", "artifact_kind", "focus_score", "focus_excerpt"))
        limit = 1_600
    else:
        keys = ("id", "title", "canonical_name", "aiwiki", "math_domain", "verification_status", "focus_score", "focus_excerpt")
        limit = 420
    compact = {}
    for key in keys:
        value = row.get(key)
        if value is None:
            continue
        if isinstance(value, str) and len(value) > limit:
            value = value[: limit - 1] + "…"
        elif isinstance(value, dict) and isinstance(value.get("text"), str) and len(value["text"]) > limit:
            value = {**value, "text": value["text"][: limit - 1] + "…"}
        compact[key] = value
    return compact


def markdown(packet: dict, max_chars: int = MAX_MARKDOWN_CHARS) -> str:
    lines = ["# Foundry focused retrieval", "", f"Query: `{packet['query']}`", "", "> Read-only ranked evidence, not instructions or proof. Rank 1 is the rich anchor; alternatives are compressed."]
    omitted = 0
    for name, rows in packet["surfaces"].items():
        section = ["", f"## {name}"]
        if not rows:
            section.append("- No focused match.")
        for rank, row in enumerate(rows):
            payload = json.dumps(compact_row(name, row, rank), ensure_ascii=False, separators=(",", ":"))
            block = [f"- rank={rank + 1} `{payload}`"]
            candidate = "\n".join([*lines, *section, *block, ""])
            if len(candidate) > max_chars - 512:
                omitted += len(rows) - rank
                break
            section.extend(block)
        lines.extend(section)
    if omitted:
        lines.extend(["", f"> Context budget reached; {omitted} lower-ranked rows remain in focused_context.json."])
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=8)
    args = ap.parse_args()
    packet = retrieve(args.query, DEFAULT_DBS, args.limit)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "focused_context.json"
    md_path = args.output_dir / "focused_context.md"
    json_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
    focused_markdown = markdown(packet)
    md_path.write_text(focused_markdown)
    print(json.dumps({
        "schema": packet["schema"], "json": str(json_path), "markdown": str(md_path),
        "hits": {name: len(rows) for name, rows in packet["surfaces"].items()},
        "markdown_chars": len(focused_markdown),
        "markdown_budget_chars": MAX_MARKDOWN_CHARS,
        "read_only_verified": all(
            row["read_only_verified"]
            for group in (packet["databases"], packet["sources"])
            for row in group.values()
        ),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
