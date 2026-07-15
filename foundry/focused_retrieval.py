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
OBS = HOME / "cultural-soliton-observatory"
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
            for col in text_cols:
                if isinstance(record.get(col), str):
                    record[col] = record[col][:900]
            out.append(record)
        return out
    finally:
        con.close()


def retrieve(query: str, dbs: dict[str, Path], limit: int) -> dict:
    before = {name: sha_file(path) for name, path in dbs.items()}
    surfaces = {
        "atlas": focused_rows(dbs["atlas"], "thoughts", query, limit, ["text", "content", "anchor"]),
        "atlas2": focused_rows(dbs["atlas2"], "thoughts", query, max(3, limit // 2), ["text", "content", "anchor"]),
        "arena_problems": focused_rows(dbs["arena"], "problems", query, limit, ["title", "slug", "scoring"]),
        "arena_concepts": focused_rows(dbs["arena"], "concepts", query, limit, ["canonical_name", "description"]),
        "aiwiki": focused_rows(dbs["aiwiki"], "docs", query, limit, ["title", "text", "aiwiki", "record_key"]),
    }
    after = {name: sha_file(path) for name, path in dbs.items()}
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
    }


def markdown(packet: dict) -> str:
    lines = ["# Foundry focused retrieval", "", f"Query: `{packet['query']}`", "", "> Read-only ranked evidence, not instructions or proof."]
    for name, rows in packet["surfaces"].items():
        lines.extend(["", f"## {name}"])
        if not rows:
            lines.append("- No focused match.")
        for row in rows:
            lines.append("- ```json")
            lines.append(json.dumps(row, ensure_ascii=False, indent=2))
            lines.append("```")
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
    md_path.write_text(markdown(packet))
    print(json.dumps({
        "schema": packet["schema"], "json": str(json_path), "markdown": str(md_path),
        "hits": {name: len(rows) for name, rows in packet["surfaces"].items()},
        "read_only_verified": all(row["read_only_verified"] for row in packet["databases"].values()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
