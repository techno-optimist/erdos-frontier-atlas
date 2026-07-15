#!/usr/bin/env python3
"""P42 Foundry: typed receipts, stall gating, frontier consultation and publish.

The script is dependency-free at runtime. It never edits canonical Atlas
records and stages only ``progress/`` during publication.
"""
from __future__ import annotations

import argparse
import difflib
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib import request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "progress"
RECEIPTS = PROGRESS / "receipts"
INDEX = PROGRESS / "index.json"
CONFIG = ROOT / "foundry" / "config.json"
LABELS = ("Frontier", "Action", "Verified", "Result", "Next gate", "Boundary held")
BLOCKED = ("blocked", "no changed condition", "selector-repeat", "selector repeat", "cannot run", "unavailable")
NEGATIVE = (
    "negative result", "negative-result", "local-exhaustion", "local exhaustion",
    "no disagreement", "prior verdict holds", "route closed", "lane remains closed",
    "no mathematical progress", "standing rotation", "no-signal", "no signal",
    "control_plane_only", "control-plane only", "inconclusive", "no witness found",
    "no witness was found", "bracket is unchanged", "bracket remains",
)
FORBIDDEN_PUBLIC = (
    re.compile(r"/(?:home|Users|private|tmp)/"),
    re.compile(r"\b(?:sk|ghp|github_pat)-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]+", re.I),
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None = None) -> str:
    return (dt or utcnow()).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def parse_sections(text: str) -> dict[str, str]:
    response = text.rsplit("## Response", 1)[-1]
    marks = list(re.finditer(r"(?m)^\*\*(Frontier|Action|Verified|Result|Next gate|Boundary held)\*\*\s*$", response))
    sections: dict[str, str] = {}
    for i, match in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(response)
        value = response[match.end():end]
        if i + 1 == len(marks):
            # Hermes may append non-agent mutation diagnostics after the final
            # labelled field. The public contract is exactly the six fields;
            # thematic-break/system postambles remain private raw provenance.
            value = re.split(r"(?m)^\s*---\s*$|^⚠️ File-mutation verifier:", value, maxsplit=1)[0]
        sections[match.group(1)] = value.strip().strip("-").strip()
    missing = [label for label in LABELS if not sections.get(label)]
    if missing:
        rows = {}
        for match in re.finditer(r"(?m)^\|\s*\*\*([^*]+)\*\*\s*\|\s*(.*?)\s*\|\s*$", response):
            rows[match.group(1).strip().lower()] = match.group(2).strip()
        needed = {"lane", "action taken", "reproduce verifier", "status", "next gate"}
        if not needed.issubset(rows):
            raise ValueError("missing required receipt labels: " + ", ".join(missing))
        sections = {
            "Frontier": rows["lane"],
            "Action": rows["action taken"],
            "Verified": "; ".join(filter(None, [rows.get("reproduce verifier"), "changed conditions: " + rows.get("changed conditions", "unknown")])),
            "Result": "; ".join(filter(None, [rows["status"], "blocked: " + rows.get("blocked", "unknown")])),
            "Next gate": rows["next gate"],
            "Boundary held": "No production Atlas writes, external submissions, git pushes, or training; cockpit fallback parsed deterministically.",
        }
    return sections


def classify(result: str, action: str) -> str:
    low = f"{result} {action}".lower()
    if any(marker in low for marker in BLOCKED):
        return "blocked"
    if any(marker in low for marker in NEGATIVE):
        return "negative_result"
    return "progress"


def parse_run_time(text: str, fallback: datetime, source_timezone: str = "America/Denver") -> str:
    match = re.search(r"^\*\*Run Time:\*\* (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$", text, re.M)
    if not match:
        return iso(fallback)
    local = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=ZoneInfo(source_timezone))
    candidate = local.astimezone(timezone.utc)
    # Cron output carries no UTC offset. Fail over to the source file's absolute
    # mtime when the configured wall-clock zone disagrees materially; this
    # catches fixed-MST hosts accidentally interpreted as DST-aware Denver.
    if abs((candidate - fallback.astimezone(timezone.utc)).total_seconds()) > 30 * 60:
        return iso(fallback.astimezone(timezone.utc))
    return iso(candidate)


def build_receipt(source: Path, job_id: str, source_timezone: str = "America/Denver") -> dict:
    raw = source.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    sections = parse_sections(text)
    content = {key: sections[label] for key, label in (
        ("frontier", "Frontier"), ("action", "Action"), ("verified", "Verified"),
        ("result", "Result"), ("next_gate", "Next gate"), ("boundary_held", "Boundary held"),
    )}
    stable = json.dumps(content, ensure_ascii=False, sort_keys=True).encode()
    occurred_at = parse_run_time(text, datetime.fromtimestamp(source.stat().st_mtime, timezone.utc), source_timezone)
    source_sha = sha(raw)
    occurrence = stable + b"\0" + occurred_at.encode() + b"\0" + job_id.encode() + b"\0" + source_sha.encode()
    receipt = {
        "schema": "p42-foundry-receipt-v1",
        "receipt_id": "sha256:" + sha(occurrence),
        "content_digest": "sha256:" + sha(stable),
        "occurred_at": occurred_at,
        **content,
        "classification": classify(content["result"], content["action"]),
        "evidence_class": "provisional",
        "source": {"job_id": job_id, "run_file": source.name, "sha256": source_sha},
    }
    pre_response = text.split("## Response", 1)[0]
    frontier_id = re.search(r'"frontier_id"\s*:\s*"([a-z0-9][a-z0-9._-]{1,127})"', pre_response, re.I)
    if frontier_id:
        receipt["frontier_id"] = frontier_id.group(1).lower()
    advice = re.search(r"Frontier advice:\s*(sha256:[a-f0-9]{64});\s*executed=(yes|no);\s*outcome=([^\n]+)", content["verified"], re.I)
    if advice:
        receipt["frontier_consult"] = {
            "advice_digest": advice.group(1).lower(),
            "executed": advice.group(2).lower() == "yes",
            "outcome": advice.group(3).strip(),
        }
    return receipt


def receipt_files() -> list[Path]:
    return sorted(RECEIPTS.glob("**/*.json")) if RECEIPTS.exists() else []


def validate_receipt(r: dict) -> list[str]:
    errors = []
    required = {"schema", "receipt_id", "content_digest", "occurred_at", "frontier", "action", "verified", "result", "next_gate", "boundary_held", "classification", "evidence_class", "source"}
    optional = {"frontier_consult", "frontier_id"}
    extra = set(r) - required - optional
    missing = required - set(r)
    if missing: errors.append("missing fields: " + ", ".join(sorted(missing)))
    if extra: errors.append("extra fields: " + ", ".join(sorted(extra)))
    if r.get("schema") != "p42-foundry-receipt-v1": errors.append("bad schema")
    if r.get("classification") not in {"progress", "negative_result", "blocked"}: errors.append("bad classification")
    expected_classification = classify(str(r.get("result", "")), str(r.get("action", "")))
    if r.get("classification") != expected_classification: errors.append(f"classification mismatch: expected {expected_classification}")
    if r.get("evidence_class") != "provisional": errors.append("receipt must remain provisional")
    if "frontier_id" in r and not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,127}", str(r["frontier_id"])): errors.append("bad frontier_id")
    consult = r.get("frontier_consult")
    if consult is not None:
        if set(consult) != {"advice_digest", "executed", "outcome"}: errors.append("bad frontier_consult fields")
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", str(consult.get("advice_digest", ""))): errors.append("bad frontier advice digest")
        if not isinstance(consult.get("executed"), bool): errors.append("bad frontier advice executed flag")
        if not isinstance(consult.get("outcome"), str) or not consult["outcome"].strip(): errors.append("empty frontier advice outcome")
        elif any(pattern.search(consult["outcome"]) for pattern in FORBIDDEN_PUBLIC): errors.append("public membrane violation in frontier advice outcome")
    for key in ("frontier", "action", "verified", "result", "next_gate", "boundary_held"):
        if not isinstance(r.get(key), str) or not r[key].strip(): errors.append(f"empty {key}")
        elif any(pattern.search(r[key]) for pattern in FORBIDDEN_PUBLIC): errors.append(f"public membrane violation in {key}")
    stable = json.dumps({key: r.get(key) for key in ("frontier", "action", "verified", "result", "next_gate", "boundary_held")}, ensure_ascii=False, sort_keys=True).encode()
    if r.get("content_digest") != "sha256:" + sha(stable): errors.append("content digest mismatch")
    src = r.get("source", {})
    if not re.fullmatch(r"[a-f0-9]{12}", str(src.get("job_id", ""))): errors.append("bad source job id")
    if Path(str(src.get("run_file", ""))).name != src.get("run_file"): errors.append("source run_file must be a basename")
    occurrence = stable + b"\0" + str(r.get("occurred_at", "")).encode() + b"\0" + str(src.get("job_id", "")).encode() + b"\0" + str(src.get("sha256", "")).encode()
    if r.get("receipt_id") != "sha256:" + sha(occurrence): errors.append("receipt occurrence digest mismatch")
    return errors


def semantic_contract_errors(r: dict, config: dict) -> list[str]:
    contract = config.get("semantic_contracts", {}).get(r.get("frontier_id"))
    if not contract or str(r.get("occurred_at", "")) < str(contract.get("effective_after", "")):
        return []
    evidence = " ".join(str(r.get(key, "")) for key in ("action", "verified")).lower()
    # A quantity substitution in an evidence bullet is still a public claim.
    # Scan the full claim-bearing membrane, not only Result and Next gate.
    claims = " ".join(
        str(r.get(key, ""))
        for key in ("frontier", "action", "verified", "result", "next_gate")
    ).lower()
    errors = []
    required = [phrase.lower() for phrase in contract.get("required_evidence_any", [])]
    if required and not any(phrase in evidence for phrase in required):
        errors.append("semantic contract missing target-quantity evidence: " + contract["target_quantity"])
    for pattern in contract.get("forbidden_claim_patterns", []):
        if re.search(pattern, claims, re.I):
            errors.append("semantic contract quantity-conflation claim: " + pattern)
    return errors


def inspect_source(source: Path, job_id: str, config: dict) -> dict:
    """Parse and validate a raw run without mutating the public progress tree."""
    source_sha = sha(source.read_bytes())
    try:
        receipt = build_receipt(
            source, job_id, config.get("source_timezone", "America/Denver")
        )
        errors = validate_receipt(receipt) + semantic_contract_errors(receipt, config)
        summary = {
            key: receipt.get(key)
            for key in ("receipt_id", "frontier_id", "classification", "occurred_at")
        }
    except Exception as exc:
        errors = [type(exc).__name__ + ": " + str(exc)]
        summary = None
    return {
        "schema": "p42-foundry-inspection-v1",
        "inspected_at": iso(),
        "valid": not errors,
        "source_sha256": source_sha,
        "receipt": summary,
        "errors": errors,
    }


def rebuild_index() -> dict:
    rows = [load_json(p) for p in receipt_files()]
    counts = Counter(r["classification"] for r in rows)
    value = {
        "schema": "p42-foundry-index-v1", "receipt_count": len(rows),
        "classifications": {k: counts.get(k, 0) for k in ("progress", "negative_result", "blocked")},
        "last_receipt": rows[-1]["receipt_id"] if rows else None,
        "updated_at": max((r["occurred_at"] for r in rows), default=None),
    }
    atomic_json(INDEX, value)
    return value


def ingest(source: Path, job_id: str, source_timezone: str = "America/Denver") -> tuple[Path, bool]:
    receipt = build_receipt(source, job_id, source_timezone)
    suffix = receipt["receipt_id"].split(":", 1)[1][:12]
    timestamp = receipt["occurred_at"].replace("-", "").replace(":", "")
    dest = RECEIPTS / receipt["occurred_at"][:4] / receipt["occurred_at"][5:7] / f"{timestamp}_{job_id}_{suffix}.json"
    if dest.exists():
        return dest, False
    errors = validate_receipt(receipt) + semantic_contract_errors(receipt, load_json(CONFIG))
    if errors: raise ValueError("; ".join(errors))
    atomic_json(dest, receipt)
    rebuild_index()
    return dest, True


def norm(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def stall_gate(state_path: Path, config: dict, frontier_id: str | None = None) -> dict:
    rows = [load_json(p) for p in receipt_files()]
    if frontier_id:
        rows = [row for row in rows if row.get("frontier_id") == frontier_id]
    rows = rows[-int(config["stall_window"]):]
    terminal = []
    for row in reversed(rows):
        if row["classification"] not in {"blocked", "negative_result"}: break
        terminal.append(row)
    terminal.reverse()
    repeated_frontier = False
    repeated_move = False
    if len(terminal) >= 2:
        a, b = terminal[-2:]
        structured_match = bool(a.get("frontier_id") and a.get("frontier_id") == b.get("frontier_id"))
        repeated_frontier = structured_match or difflib.SequenceMatcher(None, norm(a["frontier"]), norm(b["frontier"])).ratio() >= 0.75
        repeated_move = difflib.SequenceMatcher(None, norm(a["result"] + " " + a["next_gate"]), norm(b["result"] + " " + b["next_gate"])).ratio() >= 0.80
    stuck = len(terminal) >= int(config["stall_threshold"]) and (repeated_frontier or repeated_move)
    state = load_json(state_path) if state_path.exists() else {"calls": []}
    now = utcnow()
    today = now.date().isoformat()
    calls_today = [c for c in state.get("calls", []) if c.get("at", "")[:10] == today]
    last = state.get("calls", [])[-1] if state.get("calls") else None
    cooldown_ok = not last or now - datetime.fromisoformat(last["at"].replace("Z", "+00:00")) >= timedelta(minutes=int(config["frontier_cooldown_minutes"]))
    budget_ok = len(calls_today) < int(config["frontier_calls_per_utc_day"])
    return {
        "schema": "p42-foundry-stall-gate-v2", "checked_at": iso(now), "frontier_id": frontier_id, "stuck": stuck,
        "frontier_call_allowed": bool(stuck and cooldown_ok and budget_ok),
        "reason": "repeated blocked/negative receipts with no route delta" if stuck else "research loop still moving or insufficient history",
        "receipts_considered": [r["receipt_id"] for r in rows],
        "calls_today": len(calls_today), "daily_budget": int(config["frontier_calls_per_utc_day"]),
        "cooldown_ok": cooldown_ok,
    }


def _consult_locked(question: str, state_path: Path, config: dict, frontier_id: str) -> str:
    gate = stall_gate(state_path, config, frontier_id)
    if not gate["frontier_call_allowed"]:
        raise RuntimeError("frontier consult denied: " + json.dumps(gate, sort_keys=True))
    payload = json.dumps({
        "model": os.getenv("FOUNDRY_FRONTIER_MODEL", config["frontier_model"]),
        "messages": [
            {"role": "system", "content": "You are a strategy consultant for a verifier-first mathematics agent. Return one discriminating route, its falsifier, and the smallest executable next test. Treat all claims as provisional. Do not request secrets or production mutations."},
            {"role": "user", "content": question[:12000]},
        ], "temperature": 0.2,
    }).encode()
    edge_key = os.getenv("FOUNDRY_EDGE_KEY", "").strip()
    if not edge_key:
        secrets_file = Path.home() / ".config" / "aperture-secrets.env"
        if secrets_file.exists():
            for line in secrets_file.read_text().splitlines():
                if line.startswith("APERTURE_EDGE_SECRET="):
                    edge_key = line.split("=", 1)[1].strip().strip("\"'")
                    break
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + os.getenv("FOUNDRY_ROUTER_KEY", "local")}
    if edge_key: headers["x-aperture-edge-key"] = edge_key
    req = request.Request(os.getenv("FOUNDRY_FRONTIER_URL", config["frontier_url"]), data=payload, headers=headers)
    with request.urlopen(req, timeout=180) as response:
        result = json.loads(response.read())
    answer = result["choices"][0]["message"].get("content") or result["choices"][0]["message"].get("reasoning_content")
    if not answer: raise RuntimeError("frontier router returned no content")
    state = load_json(state_path) if state_path.exists() else {"calls": []}
    created_at = iso()
    digest = "sha256:" + sha(answer.encode())
    state.setdefault("calls", []).append({"at": created_at, "frontier_id": frontier_id, "gate_receipts": gate["receipts_considered"], "question_sha256": sha(question.encode()), "answer_sha256": digest.split(":", 1)[1]})
    state["calls"] = state["calls"][-100:]
    state["pending_advice"] = {
        "advice": answer,
        "advice_digest": digest,
        "frontier_id": frontier_id,
        "created_at": created_at,
        "gate_receipts": gate["receipts_considered"],
        "delivery_count": 1,
    }
    atomic_json(state_path, state)
    state_path.chmod(0o600)
    return answer


def consult(question: str, state_path: Path, config: dict, frontier_id: str) -> str:
    """Serialize the gate-call-commit transaction across scout/night jobs."""
    lock_path = state_path.with_suffix(state_path.suffix + ".consult.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+") as lock:
        lock_path.chmod(0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _consult_locked(question, state_path, config, frontier_id)


def take_pending_advice(state_path: Path, frontier_id: str) -> dict:
    """Deliver private advice until a public receipt proves it was executed."""
    state = load_json(state_path) if state_path.exists() else {"calls": []}
    if state_path.exists():
        state_path.chmod(0o600)
    pending = state.get("pending_advice")
    if not pending:
        return {"strategy_advice": None, "strategy_status": "none"}
    if pending.get("frontier_id") != frontier_id:
        return {"strategy_advice": None, "strategy_status": "pinned_elsewhere", "pinned_frontier_id": pending.get("frontier_id")}
    digest = pending.get("advice_digest")
    traces = [load_json(path).get("frontier_consult") for path in receipt_files()]
    traces = [row for row in traces if row and row.get("advice_digest") == digest]
    if any(row.get("executed") is True for row in traces):
        state["last_consumed_advice"] = {
            "advice_digest": digest,
            "consumed_at": iso(),
            "outcome": next(row["outcome"] for row in reversed(traces) if row.get("executed") is True),
        }
        state.pop("pending_advice", None)
        atomic_json(state_path, state)
        state_path.chmod(0o600)
        return {"strategy_advice": None, "strategy_status": "consumed", "strategy_digest": digest}
    pending["delivery_count"] = int(pending.get("delivery_count", 0)) + 1
    pending["last_delivered_at"] = iso()
    atomic_json(state_path, state)
    state_path.chmod(0o600)
    return {
        "strategy_advice": pending["advice"],
        "strategy_status": "pending",
        "strategy_digest": digest,
        "delivery_count": pending["delivery_count"],
    }


def acknowledge_call_incident(state_path: Path, answer_sha256: str, consulted_frontier_id: str) -> dict:
    state = load_json(state_path)
    receipts = {load_json(path)["receipt_id"]: load_json(path) for path in receipt_files()}
    for call in state.get("calls", []):
        if call.get("answer_sha256") != answer_sha256:
            continue
        certified_ids = sorted({receipts[rid].get("frontier_id") for rid in call.get("gate_receipts", []) if rid in receipts and receipts[rid].get("frontier_id")})
        call["incident"] = {
            "schema": "p42-foundry-call-incident-v1",
            "kind": "cross_frontier_global_gate",
            "acknowledged_at": iso(),
            "consulted_frontier_id": consulted_frontier_id,
            "gate_receipt_frontier_ids": certified_ids,
            "remediation": "lane-scoped stall gate v2; historical call excluded from completion evidence",
        }
        atomic_json(state_path, state)
        state_path.chmod(0o600)
        return call["incident"]
    raise RuntimeError("frontier call not found for answer hash")


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=check)


def validate() -> None:
    errors = []
    seen = set()
    for path in receipt_files():
        row = load_json(path)
        for err in validate_receipt(row) + semantic_contract_errors(row, load_json(CONFIG)):
            errors.append(f"{path.relative_to(ROOT)}: {err}")
        if row.get("receipt_id") in seen: errors.append(f"{path.relative_to(ROOT)}: duplicate receipt")
        seen.add(row.get("receipt_id"))
    expected = load_json(INDEX)
    rows = [load_json(p) for p in receipt_files()]
    counts = Counter(r["classification"] for r in rows)
    if expected.get("receipt_count") != len(rows): errors.append("progress/index.json receipt_count drift")
    if expected.get("classifications") != {k: counts.get(k, 0) for k in ("progress", "negative_result", "blocked")}: errors.append("progress/index.json classification drift")
    atlas = run([sys.executable, "tools/validate_atlas.py"], check=False)
    if atlas.returncode: errors.append("atlas validation failed:\n" + atlas.stdout)
    if errors: raise SystemExit("\n".join(errors))
    print(f"foundry validation OK: {len(rows)} receipts; atlas validation OK")


def publish(branch: str) -> None:
    validate()
    status = run(["git", "status", "--short", "--", "progress"]).stdout.strip()
    committed = False
    count = load_json(INDEX)["receipt_count"]
    if status:
        run(["git", "add", "--", "progress"])
        staged = run(["git", "diff", "--cached", "--name-only"]).stdout.splitlines()
        if any(not p.startswith("progress/") for p in staged):
            raise SystemExit("refusing publish: staged path outside progress/")
        run(["git", "commit", "-m", f"foundry: publish progress receipt {count}"])
        committed = True
    head = run(["git", "rev-parse", "HEAD"]).stdout.strip()
    remote_line = run(["git", "ls-remote", "origin", f"refs/heads/{branch}"], check=False).stdout.strip()
    remote = remote_line.split()[0] if remote_line else None
    if remote != head:
        run(["git", "push", "origin", f"HEAD:{branch}"])
        print(json.dumps({"published": True, "committed": committed, "retried_pending_push": not committed, "branch": branch, "receipt_count": count, "sha": head}))
        return
    print(json.dumps({"published": False, "committed": committed, "reason": "remote already current", "branch": branch, "receipt_count": count, "sha": head}))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=CONFIG)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("ingest"); p.add_argument("source", type=Path); p.add_argument("--job-id", required=True)
    p = sub.add_parser("inspect"); p.add_argument("source", type=Path); p.add_argument("--job-id", required=True)
    p = sub.add_parser("gate"); p.add_argument("--state", type=Path, required=True); p.add_argument("--frontier-id")
    p = sub.add_parser("consult"); p.add_argument("question"); p.add_argument("--state", type=Path, required=True); p.add_argument("--frontier-id", required=True)
    p = sub.add_parser("pending"); p.add_argument("--state", type=Path, required=True); p.add_argument("--frontier-id", required=True)
    p = sub.add_parser("ack-incident"); p.add_argument("--state", type=Path, required=True); p.add_argument("--answer-sha256", required=True); p.add_argument("--consulted-frontier-id", required=True)
    sub.add_parser("validate")
    p = sub.add_parser("publish"); p.add_argument("--branch")
    args = parser.parse_args()
    config = load_json(args.config)
    if args.command == "ingest":
        path, created = ingest(args.source, args.job_id, config.get("source_timezone", "America/Denver")); print(json.dumps({"path": str(path), "created": created}))
    elif args.command == "inspect": print(json.dumps(inspect_source(args.source, args.job_id, config), indent=2))
    elif args.command == "gate": print(json.dumps(stall_gate(args.state, config, args.frontier_id), indent=2))
    elif args.command == "consult": print(consult(args.question, args.state, config, args.frontier_id))
    elif args.command == "pending": print(json.dumps(take_pending_advice(args.state, args.frontier_id), ensure_ascii=False, indent=2))
    elif args.command == "ack-incident": print(json.dumps(acknowledge_call_incident(args.state, args.answer_sha256, args.consulted_frontier_id), indent=2))
    elif args.command == "validate": validate()
    elif args.command == "publish": publish(args.branch or config["publication_branch"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
