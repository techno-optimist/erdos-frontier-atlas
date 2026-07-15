#!/usr/bin/env python3
"""Ingest completed CHRONOS runs, expose the stall gate, and publish receipts."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PUBLIC_TEMPLATE_PLACEHOLDER = re.compile(r"<[^<>\n]{2,240}>")
EFFICIENCY_PARSER = Path(__file__).with_name("foundry_efficiency.py")


def parser_source_digest() -> str:
    return "sha256:" + hashlib.sha256(EFFICIENCY_PARSER.read_bytes()).hexdigest()


def telemetry_contract_digest(config: dict) -> str:
    canonical = json.dumps(
        {
            "runtime_budget": config.get("runtime_budget"),
            "parser_source_sha256": parser_source_digest(),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def semantic_contract_digest(config: dict) -> str:
    canonical = json.dumps(
        {
            "semantic_contracts": config.get("semantic_contracts", {}),
            "milestone_policy": config.get("milestone_policy", {}),
            "runtime_budget": config.get("runtime_budget"),
            "runtime_telemetry_contract_digest": telemetry_contract_digest(config),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def runtime_budget_digest(config: dict) -> str | None:
    budget = config.get("runtime_budget")
    if not isinstance(budget, dict):
        return None
    canonical = json.dumps(
        budget, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def parse_time(value: str | None) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(
            timezone.utc
        )
    except (TypeError, ValueError):
        return None


def runtime_budget_assessment(
    receipt: dict, efficiency: dict | None, config: dict, source_job_id: str | None = None
) -> tuple[list[str], dict | None]:
    """Bind a source occurrence to trusted first-turn resource telemetry."""
    budget = config.get("runtime_budget")
    if not isinstance(budget, dict):
        return [], None
    occurred = parse_time(receipt.get("occurred_at"))
    effective = parse_time(budget.get("effective_after"))
    if occurred is None:
        return ["runtime budget cannot parse receipt occurrence time"], None
    if effective and occurred < effective:
        return [], {"status": "grandfathered_before_runtime_budget"}

    expected_digest = runtime_budget_digest(config)
    if not isinstance(efficiency, dict):
        return ["trusted runtime telemetry unavailable for source occurrence"], None
    if efficiency.get("runtime_budget_digest") != expected_digest:
        return ["runtime telemetry policy digest does not match publisher policy"], {
            "status": "policy_digest_mismatch",
            "expected_runtime_budget_digest": expected_digest,
            "observed_runtime_budget_digest": efficiency.get("runtime_budget_digest"),
        }
    expected_telemetry_digest = telemetry_contract_digest(config)
    if efficiency.get("telemetry_contract_digest") != expected_telemetry_digest:
        return ["runtime telemetry parser contract does not match publisher policy"], {
            "status": "telemetry_contract_mismatch",
            "expected_telemetry_contract_digest": expected_telemetry_digest,
            "observed_telemetry_contract_digest": efficiency.get(
                "telemetry_contract_digest"
            ),
        }

    # The raw six-label draft does not own source metadata. Bind to the
    # operator-known cron directory/job argument; receipt source is only a
    # compatibility fallback for already-ingested fixtures.
    job_id = source_job_id or receipt.get("source", {}).get("job_id")
    window = int(budget.get("receipt_match_window_seconds", 300))
    candidates = []
    for session in efficiency.get("sessions", []):
        ended = parse_time(session.get("ended_at"))
        if (
            session.get("status") != "complete"
            or session.get("job_id") != job_id
            or ended is None
        ):
            continue
        delta = abs((occurred - ended).total_seconds())
        if delta <= window:
            candidates.append((delta, str(session.get("session_id", "")), session))
    if not candidates:
        return ["trusted complete runtime session unavailable for source occurrence"], {
            "status": "no_complete_session_match",
            "job_id": job_id,
            "match_window_seconds": window,
        }
    delta, _, session = min(candidates, key=lambda row: (row[0], row[1]))
    threshold = float(budget["expensive_terminal_seconds"])
    expensive = [
        row for row in session.get("expensive_terminal_calls", [])
        if float(row.get("duration_seconds", 0)) > threshold
    ]
    observed = {
        "api_call_count": int(session.get("api_call_count", 0)),
        "max_input_tokens": int(session.get("max_input_tokens", 0)),
        "context_growth_tokens": int(session.get("context_growth_tokens", 0)),
        "wall_seconds": session.get("wall_seconds"),
        "expensive_terminal_call_count": len(expensive),
        "token_accounting_consistent": session.get("token_accounting_consistent") is True,
    }
    limits = {
        key: budget[key] for key in (
            "max_api_calls", "max_input_tokens", "max_context_growth_tokens",
            "max_wall_seconds", "expensive_terminal_seconds",
            "max_expensive_terminal_calls",
        )
    }
    errors = []
    for metric, limit_key in (
        ("api_call_count", "max_api_calls"),
        ("max_input_tokens", "max_input_tokens"),
        ("context_growth_tokens", "max_context_growth_tokens"),
        ("wall_seconds", "max_wall_seconds"),
        ("expensive_terminal_call_count", "max_expensive_terminal_calls"),
    ):
        value = observed[metric]
        if value is None or float(value) > float(budget[limit_key]):
            errors.append(
                f"runtime budget exceeded: {metric}={value} > {limit_key}={budget[limit_key]}"
            )
    if not observed["token_accounting_consistent"]:
        errors.append("runtime budget telemetry has inconsistent token accounting")
    evidence = {
        "status": "over_budget" if errors else "within_budget",
        "runtime_budget_digest": expected_digest,
        "telemetry_contract_digest": expected_telemetry_digest,
        "session_id": session.get("session_id"),
        "source_end_delta_seconds": round(delta, 3),
        "observed": observed,
        "limits": limits,
    }
    return errors, evidence


def apply_runtime_budget(
    inspection: dict, efficiency: dict | None, config: dict,
    source_job_id: str | None = None,
) -> dict:
    if not inspection.get("valid"):
        return inspection
    errors, evidence = runtime_budget_assessment(
        inspection.get("receipt") or {}, efficiency, config, source_job_id
    )
    if evidence is not None:
        inspection["runtime_telemetry"] = evidence
    if errors:
        inspection["valid"] = False
        inspection.setdefault("errors", []).extend(errors)
    return inspection


def rejection_feedback_is_current(
    detail: dict, source_sha: str, contract_digest: str
) -> bool:
    return bool(
        detail.get("source_sha256") == source_sha
        and detail.get("semantic_contract_digest") == contract_digest
    )


def source_is_watermarked(state: dict, key: str, source_sha: str) -> bool:
    """Return true only when this exact immutable source was already handled."""
    return any(state.get(bucket, {}).get(key) == source_sha for bucket in ("accepted", "rejected"))


def inspect_run(tool: Path, source: Path, job_id: str, repo: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(tool), "inspect", str(source), "--job-id", job_id],
        cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        value = json.loads(proc.stdout)
    except (TypeError, ValueError):
        value = {
            "schema": "p42-foundry-inspection-v1", "valid": False,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "receipt": None,
            "errors": [proc.stderr.strip().splitlines()[-1][:500] if proc.stderr.strip() else "inspection failed"],
        }
    return value


def rejection_detail(
    inspection: dict, fallback_reason: str, contract_digest: str | None = None
) -> dict:
    receipt = inspection.get("receipt") or {}
    errors = [str(row)[:500] for row in inspection.get("errors", []) if str(row).strip()]
    runtime_rejection = bool(inspection.get("runtime_telemetry")) or any(
        str(error).startswith(("runtime ", "trusted runtime "))
        for error in errors
    )
    detail = {
        "schema": "p42-foundry-quarantine-feedback-v1",
        "recorded_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_sha256": inspection.get("source_sha256"),
        "receipt_id": receipt.get("receipt_id"),
        "frontier_id": receipt.get("frontier_id"),
        "classification": receipt.get("classification"),
        "occurred_at": receipt.get("occurred_at"),
        "errors": errors or [fallback_reason[:500]],
        "remediation": (
            "shrink the action and context to the checked-in runtime budget, then rerun one bounded step; runtime rejection says nothing about the mathematical claim"
            if runtime_rejection
            else "replay the bounded evidence, then correct scope; never claim the quarantined receipt was published"
        ),
    }
    if contract_digest:
        detail["semantic_contract_digest"] = contract_digest
    if inspection.get("runtime_telemetry") is not None:
        detail["runtime_telemetry"] = inspection["runtime_telemetry"]
    return detail


def failed_run_reason(text: str) -> str | None:
    if re.search(r"(?m)^# Cron Job: .*\(FAILED\)\s*$", text):
        return "failed cron run is not a mathematical receipt"
    if re.search(r"(?mi)^\*\*Status:\*\*\s*(?:script failed|failed|error)\b", text):
        return "failed cron status is not a mathematical receipt"
    return None


def matching_receipt_paths(
    repo: Path, job_id: str, run_file: str, source_sha: str
) -> list[Path]:
    matches = []
    for path in (repo / "progress" / "receipts").glob("**/*.json"):
        try:
            source = json.loads(path.read_text()).get("source", {})
        except (OSError, ValueError):
            continue
        if (
            source.get("job_id") == job_id
            and source.get("run_file") == run_file
            and source.get("sha256") == source_sha
        ):
            matches.append(path)
    return sorted(matches)


def template_receipt_reason(paths: list[Path]) -> str | None:
    for path in paths:
        try:
            receipt = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        for key in ("frontier", "action", "verified", "result", "next_gate", "boundary_held"):
            value = receipt.get(key)
            if isinstance(value, str) and PUBLIC_TEMPLATE_PLACEHOLDER.fullmatch(value.strip()):
                return f"public receipt contains template placeholder in {key}"
    return None


def quarantine_invalid_accepted_sources(
    ingest_state: dict, cron_output: Path, repo: Path, tool: Path,
    contract_digest: str | None = None,
) -> list[dict]:
    """Repair older failed-envelope or template-placeholder acceptances."""
    revoked = []
    for key, source_sha in list(ingest_state.get("accepted", {}).items()):
        job_id, separator, filename = key.partition("/")
        if not separator:
            continue
        source = cron_output / job_id / filename
        raw = source.read_bytes() if source.exists() else None
        source_matches = raw is not None and hashlib.sha256(raw).hexdigest() == source_sha
        removed = matching_receipt_paths(repo, job_id, filename, source_sha)
        reason = (
            failed_run_reason(raw.decode("utf-8", errors="replace"))
            if source_matches and raw is not None else None
        ) or template_receipt_reason(removed)
        if not reason:
            continue
        if source_matches:
            inspection = inspect_run(tool, source, job_id, repo)
        else:
            receipt = json.loads(removed[0].read_text()) if removed else {}
            inspection = {
                "source_sha256": source_sha,
                "receipt": {
                    field: receipt.get(field)
                    for field in ("receipt_id", "frontier_id", "classification", "occurred_at")
                },
                "errors": [reason + "; raw source unavailable or hash-mismatched"],
            }
        for path in removed:
            path.unlink()
        ingest_state["accepted"].pop(key, None)
        ingest_state.setdefault("accepted_runtime", {}).pop(key, None)
        ingest_state.setdefault("rejected", {})[key] = source_sha
        ingest_state.setdefault("rejected_details", {})[key] = rejection_detail(
            inspection, reason, contract_digest
        )
        revoked.append({
            "run_file": filename,
            "reason": reason,
            "removed_receipts": [path.name for path in removed],
        })
    # The earliest publisher predates the private ingest ledger. Exact prompt
    # placeholders plus the receipt's immutable source tuple are sufficient to
    # quarantine those legacy rows even when both raw retention and the old
    # acceptance record are gone.
    for path in sorted((repo / "progress" / "receipts").glob("**/*.json")):
        reason = template_receipt_reason([path])
        if not reason:
            continue
        try:
            receipt = json.loads(path.read_text())
            source = receipt.get("source", {})
            job_id = source.get("job_id")
            filename = source.get("run_file")
            source_sha = source.get("sha256")
        except (OSError, ValueError):
            continue
        if (
            not re.fullmatch(r"[a-f0-9]{12}", str(job_id or ""))
            or Path(str(filename or "")).name != filename
            or not re.fullmatch(r"[a-f0-9]{64}", str(source_sha or ""))
        ):
            continue
        key = f"{job_id}/{filename}"
        accepted_sha = ingest_state.get("accepted", {}).get(key)
        ledger_key = key if accepted_sha in (None, source_sha) else f"{key}#{source_sha[:12]}"
        if accepted_sha == source_sha:
            ingest_state["accepted"].pop(key, None)
            ingest_state.setdefault("accepted_runtime", {}).pop(key, None)
        inspection = {
            "source_sha256": source_sha,
            "receipt": {
                field: receipt.get(field)
                for field in ("receipt_id", "frontier_id", "classification", "occurred_at")
            },
            "errors": [reason + "; legacy private acceptance and raw source unavailable"],
        }
        ingest_state.setdefault("rejected", {})[ledger_key] = source_sha
        ingest_state.setdefault("rejected_details", {})[ledger_key] = rejection_detail(
            inspection, reason, contract_digest
        )
        path.unlink()
        revoked.append({
            "run_file": filename,
            "reason": reason,
            "removed_receipts": [path.name],
        })
    return revoked


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--cron-output", type=Path, default=Path.home() / ".hermes" / "cron" / "output")
    ap.add_argument("--state", type=Path, default=Path.home() / ".hermes" / "chronos_state" / "foundry_frontier_budget.json")
    ap.add_argument("--ingest-state", type=Path, default=Path.home() / ".hermes" / "chronos_state" / "foundry_ingest_state.json")
    ap.add_argument("--efficiency-report", type=Path)
    ap.add_argument("--no-push", action="store_true")
    args = ap.parse_args()
    lock_path = args.state.with_name("foundry_tick.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_handle = lock_path.open("a+")
    lock_path.chmod(0o600)
    try:
        fcntl.flock(lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print(json.dumps({"skipped": True, "reason": "another Foundry tick holds the publication lock"}))
        return 0
    config = json.loads((args.repo / "foundry" / "config.json").read_text())
    contract_digest = semantic_contract_digest(config)
    efficiency = None
    if args.efficiency_report and args.efficiency_report.exists():
        efficiency = json.loads(args.efficiency_report.read_text())
    tool = args.repo / "tools" / "foundry.py"
    created = []
    rejected = []
    ingest_state = json.loads(args.ingest_state.read_text()) if args.ingest_state.exists() else {}
    ingest_state.setdefault("accepted", {})
    ingest_state.setdefault("rejected", {})
    ingest_state.setdefault("rejected_details", {})
    ingest_state.setdefault("accepted_runtime", {})
    revoked = quarantine_invalid_accepted_sources(
        ingest_state, args.cron_output, args.repo, tool, contract_digest
    )
    if any(row["removed_receipts"] for row in revoked):
        subprocess.run(
            [sys.executable, str(tool), "rebuild-index"],
            cwd=args.repo, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, check=True,
        )
    # Backfill hash-only quarantines and replay exact rejected sources whenever
    # the semantic contract changes. If a current contract accepts an old
    # source, clear its watermark so normal ingest can reconsider it below.
    for key, source_sha in list(ingest_state["rejected"].items()):
        detail = ingest_state["rejected_details"].get(key, {})
        if rejection_feedback_is_current(detail, source_sha, contract_digest):
            continue
        job_id, separator, filename = key.partition("/")
        source = args.cron_output / job_id / filename
        if not separator or not source.exists():
            ingest_state["rejected_details"][key] = rejection_detail({
                "source_sha256": source_sha,
                "receipt": None,
                "errors": ["legacy raw source unavailable; hash-only quarantine retained"],
            }, "legacy raw source unavailable", contract_digest)
            continue
        if hashlib.sha256(source.read_bytes()).hexdigest() != source_sha:
            ingest_state["rejected_details"][key] = rejection_detail({
                "source_sha256": source_sha,
                "receipt": None,
                "errors": ["legacy raw source no longer matches quarantined hash; quarantine retained"],
            }, "legacy raw source hash mismatch", contract_digest)
            continue
        inspection = apply_runtime_budget(
            inspect_run(tool, source, job_id, args.repo), efficiency, config, job_id
        )
        if inspection.get("valid"):
            ingest_state["rejected"].pop(key, None)
            ingest_state["rejected_details"].pop(key, None)
        else:
            ingest_state["rejected_details"][key] = rejection_detail(
                inspection, "ingest failed", contract_digest
            )
    for job_id in config["source_job_ids"]:
        source_dir = args.cron_output / job_id
        if not source_dir.exists(): continue
        for source in sorted(source_dir.glob("*.md")):
            source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
            key = f"{job_id}/{source.name}"
            if source_is_watermarked(ingest_state, key, source_sha):
                continue
            inspection = apply_runtime_budget(
                inspect_run(tool, source, job_id, args.repo), efficiency, config, job_id
            )
            if not inspection.get("valid"):
                detail = rejection_detail(inspection, "ingest failed", contract_digest)
                rejected.append({"run_file": source.name, "reason": detail["errors"][0][:240]})
                ingest_state["rejected"][key] = source_sha
                ingest_state["rejected_details"][key] = detail
                ingest_state["accepted"].pop(key, None)
                ingest_state["accepted_runtime"].pop(key, None)
                continue
            proc = subprocess.run([sys.executable, str(tool), "ingest", str(source), "--job-id", job_id], cwd=args.repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc.returncode == 0:
                if json.loads(proc.stdout).get("created"): created.append(source.name)
                ingest_state["accepted"][key] = source_sha
                if inspection.get("runtime_telemetry") is not None:
                    ingest_state["accepted_runtime"][key] = inspection["runtime_telemetry"]
                ingest_state["rejected"].pop(key, None)
                ingest_state["rejected_details"].pop(key, None)
            elif proc.returncode != 0:
                reason = proc.stderr.strip().splitlines()[-1][:240] if proc.stderr.strip() else "ingest failed"
                rejected.append({"run_file": source.name, "reason": reason})
                ingest_state["rejected"][key] = source_sha
                ingest_state["rejected_details"][key] = rejection_detail(
                    inspection, reason, contract_digest
                )
                ingest_state["accepted"].pop(key, None)
                ingest_state["accepted_runtime"].pop(key, None)
    args.ingest_state.parent.mkdir(parents=True, exist_ok=True)
    ingest_tmp = args.ingest_state.with_suffix(args.ingest_state.suffix + ".tmp")
    ingest_tmp.write_text(json.dumps(ingest_state, indent=2) + "\n")
    os.replace(ingest_tmp, args.ingest_state)
    args.ingest_state.chmod(0o600)
    frontier_ids = sorted({
        row.get("frontier_id")
        for path in (args.repo / "progress" / "receipts").glob("**/*.json")
        for row in [json.loads(path.read_text())]
        if row.get("frontier_id")
    })
    lane_gates = {}
    for frontier_id in frontier_ids:
        proc = subprocess.run(
            [sys.executable, str(tool), "gate", "--state", str(args.state), "--frontier-id", frontier_id],
            cwd=args.repo, text=True, stdout=subprocess.PIPE, check=True,
        )
        lane_gates[frontier_id] = json.loads(proc.stdout)
    gate = {"schema": "p42-foundry-stall-summary-v1", "lanes": lane_gates}
    gate_path = args.state.with_name("foundry_stall_gate.json")
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.write_text(json.dumps(gate, indent=2) + "\n")
    publish_result = {"published": False, "reason": "no-push mode"}
    if not args.no_push:
        published = subprocess.run([sys.executable, str(tool), "publish"], cwd=args.repo, text=True, stdout=subprocess.PIPE, check=True)
        try: publish_result = json.loads(published.stdout.strip().splitlines()[-1])
        except Exception: publish_result = {"published": False, "reason": "unparseable publisher output"}
    print(json.dumps({"ingested": created, "rejected": rejected, "revoked": revoked, "gate": gate, "publication": publish_result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
