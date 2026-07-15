#!/usr/bin/env python3
"""Deterministic CHRONOS context + Foundry frontier-advice preprocessor."""
from __future__ import annotations

import json
import hashlib
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
REPO = HOME / "erdos-frontier-atlas"
STATE = HOME / ".hermes" / "chronos_state"
MODE = "deep" if "night" in Path(__file__).name else "scout"
LIMIT = "4" if MODE == "deep" else "3"
FOCUS_LIMIT = "12" if MODE == "deep" else "8"
BUDGET = STATE / "foundry_frontier_budget.json"
CONFIG = REPO / "foundry" / "config.json"
INGEST_STATE = STATE / "foundry_ingest_state.json"


def call(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def first_allowed_stall(ranked: list[dict], gate_lookup) -> tuple[str | None, dict | None]:
    for candidate in ranked:
        candidate_id = candidate.get("frontier_id")
        gate = gate_lookup(candidate_id)
        if gate and gate.get("frontier_call_allowed"):
            return candidate_id, gate
    return None, None


def worker_instruction(original: str) -> str:
    original = original.replace("Load context_packet.md, ", "")
    return "Read focused_context.md first. Load context_packet.md only if the focused evidence cannot support the registered falsifier; record why broader context was needed. " + original


def latest_quarantine_feedback(state_path: Path, frontier_id: str) -> dict | None:
    try:
        state = json.loads(state_path.read_text())
    except (OSError, ValueError):
        return None
    rows = [
        row for row in state.get("rejected_details", {}).values()
        if row.get("schema") == "p42-foundry-quarantine-feedback-v1"
        and row.get("frontier_id") == frontier_id
        and row.get("errors")
    ]
    if not rows:
        return None
    row = sorted(rows, key=lambda value: (value.get("occurred_at") or "", value.get("recorded_at") or ""))[-1]
    return {
        key: row.get(key) for key in (
            "schema", "recorded_at", "source_sha256", "receipt_id", "frontier_id",
            "classification", "occurred_at", "errors", "remediation",
            "semantic_contract_digest",
        )
    }


def trace_receipt_contract(strategy_digest: str | None) -> dict | None:
    if not strategy_digest:
        return None
    return {
        "publication_gate": "hard_quarantine_on_missing_or_mismatched_trace",
        "copy_digest_byte_for_byte": strategy_digest,
        "verified_line_if_executed": (
            f"Frontier advice: {strategy_digest}; executed=yes; "
            "outcome=<replace with concise public-safe test result>"
        ),
        "verified_line_if_not_executed": (
            f"Frontier advice: {strategy_digest}; executed=no; "
            "outcome=<replace with concise public-safe blocker>"
        ),
    }


def main() -> int:
    private_state = json.loads(BUDGET.read_text()) if BUDGET.exists() else {}
    pinned_frontier_id = (private_state.get("pending_advice") or {}).get("frontier_id")
    if pinned_frontier_id:
        selected_frontier_id = pinned_frontier_id
        selection = {"schema": "p42-foundry-selector-v1", "selected_frontier_id": pinned_frontier_id, "reason": "pending advice pins its certified frontier until execution"}
    else:
        selector_proc = call([sys.executable, str(REPO / "foundry" / "select_frontier.py")])
        try:
            selection = json.loads(selector_proc.stdout)
            selected_frontier_id = selection["selected_frontier_id"]
        except Exception:
            print(selector_proc.stdout, end="")
            return selector_proc.returncode or 1
    selected_gate = None
    if not pinned_frontier_id:
        def gate_lookup(candidate_id):
            candidate_proc = call([sys.executable, str(REPO / "tools" / "foundry.py"), "gate", "--state", str(BUDGET), "--frontier-id", candidate_id])
            try:
                return json.loads(candidate_proc.stdout)
            except Exception:
                return None
        override_id, selected_gate = first_allowed_stall(selection.get("ranked", []), gate_lookup)
        if override_id:
            selected_frontier_id = override_id
            selection["escalation_override"] = {
                "frontier_id": override_id,
                "reason": "lane-certified stall with budget and cooldown available",
            }
    context = call([
        sys.executable, str(HOME / ".hermes" / "scripts" / "chronos_frontier_context.py"),
        "--mode", MODE, "--limit", LIMIT, "--frontier-id", selected_frontier_id,
    ])
    try:
        summary = json.loads(context.stdout)
    except Exception:
        print(context.stdout, end="")
        return context.returncode or 1
    if not summary.get("allowed"):
        print(json.dumps(summary, indent=2))
        return 0

    packet = json.loads(Path(summary["artifact_dir"]).joinpath("context_packet.json").read_text())
    item = packet.get("frontier", {})
    focus_proc = call([
        sys.executable, str(REPO / "foundry" / "focused_retrieval.py"),
        "--query", str(item.get("query") or item.get("title") or item.get("id")),
        "--output-dir", summary["artifact_dir"], "--limit", FOCUS_LIMIT,
    ])
    try:
        focus = json.loads(focus_proc.stdout)
    except Exception:
        print(focus_proc.stdout, end="")
        return focus_proc.returncode or 1
    if not focus.get("read_only_verified"):
        print(json.dumps({"error": "focused retrieval failed read-only hash verification", "focused_retrieval": focus}, indent=2))
        return 1
    summary["focused_retrieval"] = focus

    shadow_path = Path(summary["artifact_dir"]) / "shadow_policy.json"
    shadow_proc = call([
        sys.executable, str(REPO / "foundry" / "shadow_policy.py"), "--output", str(shadow_path),
    ])
    try:
        shadow = json.loads(shadow_proc.stdout)
    except Exception:
        shadow = {"policy_status": "shadow_unavailable", "error": shadow_proc.stdout[-300:]}
    selection["shadow_policy"] = shadow

    if selected_gate is None:
        gate_proc = call([sys.executable, str(REPO / "tools" / "foundry.py"), "gate", "--state", str(BUDGET), "--frontier-id", selected_frontier_id])
        try: gate = json.loads(gate_proc.stdout)
        except Exception: gate = {"frontier_call_allowed": False, "reason": "gate unavailable"}
    else:
        gate = selected_gate
    pending_proc = call([sys.executable, str(REPO / "tools" / "foundry.py"), "pending", "--state", str(BUDGET), "--frontier-id", selected_frontier_id])
    try: pending = json.loads(pending_proc.stdout)
    except Exception: pending = {"strategy_advice": None, "strategy_status": "pending_unavailable"}
    foundry = {"gate": gate, **pending}
    foundry["quarantine_feedback"] = latest_quarantine_feedback(
        INGEST_STATE, selected_frontier_id
    )
    if not foundry.get("strategy_advice") and gate.get("frontier_call_allowed"):
        question = "\n".join([
            "Verifier-first mathematics strategy consultation.",
            f"Frontier: {item.get('title') or item.get('id')}",
            f"Question: {item.get('query')}",
            f"Failed/current route: {item.get('next_action')}",
            f"Falsifier: {item.get('falsifier')}",
            f"Avoid: {item.get('avoid')}",
            "Return one route delta, its falsifier, and the smallest executable local test. No theorem claim.",
        ])
        advice = call([sys.executable, str(REPO / "tools" / "foundry.py"), "consult", "--state", str(BUDGET), "--frontier-id", selected_frontier_id, question])
        if advice.returncode == 0:
            advice_text = advice.stdout.strip()
            foundry.update(
                strategy_advice=advice_text,
                strategy_digest="sha256:" + hashlib.sha256(advice_text.encode()).hexdigest(),
                strategy_status="consulted",
                delivery_count=1,
            )
        else:
            foundry.update(strategy_status="consult_failed", error=advice.stdout.strip().splitlines()[-1][:300] if advice.stdout.strip() else "unknown")
    summary["foundry"] = foundry
    summary["foundry"]["selection"] = selection
    summary["foundry"]["receipt_contract"] = trace_receipt_contract(
        foundry.get("strategy_digest")
    )
    contract = json.loads(CONFIG.read_text()).get("semantic_contracts", {}).get(selected_frontier_id)
    summary["foundry"]["target_contract"] = contract
    summary["next_instruction"] = worker_instruction(summary["next_instruction"]) + " Preserve the exact target quantity in foundry.target_contract; a related theorem or easier quantity is not evidence. Treat foundry.strategy_advice as provisional; execute and verify its smallest test when present. If foundry.receipt_contract is present, copy its digest byte-for-byte into one typed Frontier advice line in Verified. Missing or mismatched trace is a hard publication quarantine."
    if foundry["quarantine_feedback"]:
        summary["next_instruction"] += " A prior receipt for this exact frontier was quarantined. Treat foundry.quarantine_feedback as a hard failed-publication counterexample: do not repeat or paraphrase the forbidden claim. Replay the bounded evidence before issuing a corrected receipt, state the smaller supported claim, and never imply the quarantined receipt was published."
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
