#!/usr/bin/env python3
"""Deterministic CHRONOS context + Foundry frontier-advice preprocessor."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
REPO = HOME / "erdos-frontier-atlas"
STATE = HOME / ".hermes" / "chronos_state"
MODE = "deep" if "night" in Path(__file__).name else "scout"
LIMIT = "12" if MODE == "deep" else "8"


def call(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def main() -> int:
    context = call([sys.executable, str(HOME / ".hermes" / "scripts" / "chronos_frontier_context.py"), "--mode", MODE, "--limit", LIMIT])
    try:
        summary = json.loads(context.stdout)
    except Exception:
        print(context.stdout, end="")
        return context.returncode or 1
    if not summary.get("allowed"):
        print(json.dumps(summary, indent=2))
        return 0

    gate_proc = call([sys.executable, str(REPO / "tools" / "foundry.py"), "gate", "--state", str(STATE / "foundry_frontier_budget.json")])
    try: gate = json.loads(gate_proc.stdout)
    except Exception: gate = {"frontier_call_allowed": False, "reason": "gate unavailable"}
    foundry = {"gate": gate, "strategy_advice": None, "strategy_status": "gate_closed"}
    if gate.get("frontier_call_allowed"):
        packet = json.loads(Path(summary["artifact_dir"]).joinpath("context_packet.json").read_text())
        item = packet.get("frontier", {})
        question = "\n".join([
            "Verifier-first mathematics strategy consultation.",
            f"Frontier: {item.get('title') or item.get('id')}",
            f"Question: {item.get('query')}",
            f"Failed/current route: {item.get('next_action')}",
            f"Falsifier: {item.get('falsifier')}",
            f"Avoid: {item.get('avoid')}",
            "Return one route delta, its falsifier, and the smallest executable local test. No theorem claim.",
        ])
        advice = call([sys.executable, str(REPO / "tools" / "foundry.py"), "consult", "--state", str(STATE / "foundry_frontier_budget.json"), question])
        if advice.returncode == 0:
            foundry.update(strategy_advice=advice.stdout.strip(), strategy_status="consulted")
        else:
            foundry.update(strategy_status="consult_failed", error=advice.stdout.strip().splitlines()[-1][:300] if advice.stdout.strip() else "unknown")
    summary["foundry"] = foundry
    summary["next_instruction"] += " Treat foundry.strategy_advice as provisional; execute and verify its smallest test when present."
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

