#!/usr/bin/env python3
"""One-time DGX scheduler migration for the Foundry research jobs."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[1]
CRON = HOME / ".hermes" / "cron"
JOBS = CRON / "jobs.json"
LOCK = CRON / ".jobs.lock"
TARGETS = {"50c8e4391849", "e97056701b6d"}
MODEL = "/home/chronos/models/qwen3.6-35b-a3b"
AGENT = HOME / ".local" / "bin" / "chronos-agent"
COMPACT_SKILLS = ["foundry"]
INSTALLS = {
    ROOT / "foundry" / "dgx_research_prep.py": [
        HOME / ".hermes" / "scripts" / "chronos_frontier_scout_prep.py",
        HOME / ".hermes" / "scripts" / "chronos_frontier_night_prep.py",
    ],
    ROOT / "foundry" / "dgx_tick.py": [HOME / ".hermes" / "scripts" / "erdos_foundry_tick.py"],
    ROOT / "foundry" / "SKILL.md": [HOME / ".hermes" / "skills" / "foundry" / "SKILL.md"],
}
SUFFIX = """

FOUNDRY RECURSION (operator-authorized): Use only the lane-scoped
foundry.gate in the prep output for escalation authorization. The primary
researcher for this job is the local Qwen 35B. If and only if
frontier_call_allowed is true, make exactly one strategy consultation with:
python3 ~/erdos-frontier-atlas/tools/foundry.py consult --state
~/.hermes/chronos_state/foundry_frontier_budget.json --frontier-id
'<foundry.gate.frontier_id>' '<public-safe frontier,
failed routes, falsifier, desired executable test>'. Treat its answer as
provisional strategy, execute the smallest discriminating test locally, and
verify it before reporting. Never place secrets or local paths in the six
labelled final receipt fields. Git publication is handled by a separate
no-agent membrane; do not run git here.
""".strip()
TRACE_SUFFIX = """

FOUNDRY TRACE (required): If `foundry.strategy_digest` is present in prep,
the final **Verified** section must contain this exact typed line:
`Frontier advice: <foundry.strategy_digest>; executed=yes|no;
outcome=<public-safe result>`. This line is mandatory even when the same trace
was recorded in a session artifact; only the six labelled receipt crosses the
publication membrane.
""".strip()


def append_prompt_once(prompt: str, marker: str, suffix: str) -> str:
    if marker in prompt:
        return prompt
    return prompt.rstrip() + "\n\n" + suffix


def install_runtime_files() -> dict[str, str]:
    installed = {}
    for source, targets in INSTALLS.items():
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        for target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_suffix(target.suffix + ".tmp")
            shutil.copy2(source, tmp)
            tmp.chmod(0o755 if target.suffix == ".py" else 0o644)
            os.replace(tmp, target)
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise SystemExit(f"runtime install digest mismatch: {target}")
            installed[str(target)] = digest
    return installed


def main() -> int:
    installed = install_runtime_files()
    settings = {
        "providers.foundry-qwen35b.name": "foundry-qwen35b",
        "providers.foundry-qwen35b.base_url": "http://127.0.0.1:30000/v1",
        "providers.foundry-qwen35b.api_key": "local",
        "providers.foundry-qwen35b.api_mode": "chat_completions",
        "providers.foundry-qwen35b.model": MODEL,
        "providers.foundry-qwen35b.context_length": "262144",
        "providers.foundry-qwen35b.extra_body.chat_template_kwargs.enable_thinking": "false",
        "auxiliary.compression.provider": "foundry-qwen35b",
        "auxiliary.compression.model": MODEL,
        "auxiliary.compression.base_url": "http://127.0.0.1:30000/v1",
        "auxiliary.compression.api_key": "local",
        "auxiliary.compression.timeout": "600",
        "auxiliary.compression.extra_body.chat_template_kwargs.enable_thinking": "false",
    }
    for key, value in settings.items():
        subprocess.run([str(AGENT), "config", "set", key, value], check=True, stdout=subprocess.DEVNULL)
    LOCK.touch(exist_ok=True)
    with LOCK.open("r+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data = json.loads(JOBS.read_text())
        rows = data["jobs"] if isinstance(data, dict) else data
        changed = []
        for job in rows:
            if job.get("id") not in TARGETS:
                continue
            job["provider"] = "foundry-qwen35b"
            job["model"] = MODEL
            job["base_url"] = "http://127.0.0.1:30000/v1"
            job["skill"] = "foundry"
            job["skills"] = COMPACT_SKILLS
            job["prompt"] = job.get("prompt", "").replace(
                "python3 ~/erdos-frontier-atlas/tools/foundry.py consult --state\n~/.hermes/chronos_state/foundry_frontier_budget.json '<public-safe frontier,",
                "python3 ~/erdos-frontier-atlas/tools/foundry.py consult --state\n~/.hermes/chronos_state/foundry_frontier_budget.json --frontier-id\n'<foundry.gate.frontier_id>' '<public-safe frontier,",
            )
            job["prompt"] = job["prompt"].replace(
                "FOUNDRY RECURSION (operator-authorized): Read\n~/.hermes/chronos_state/foundry_stall_gate.json before choosing the action. The\nprimary researcher",
                "FOUNDRY RECURSION (operator-authorized): Use only the lane-scoped\nfoundry.gate in the prep output for escalation authorization. The primary\nresearcher",
            )
            if job["id"] == "50c8e4391849":
                job["schedule"] = {"kind": "interval", "minutes": 30, "display": "every 30m"}
                job["schedule_display"] = "every 30m"
            job["prompt"] = append_prompt_once(
                job.get("prompt", ""), "FOUNDRY RECURSION (operator-authorized)", SUFFIX
            )
            job["prompt"] = append_prompt_once(
                job["prompt"], "FOUNDRY TRACE (required)", TRACE_SUFFIX
            )
            changed.append(job["id"])
        if changed != sorted(TARGETS):
            raise SystemExit(f"expected jobs {sorted(TARGETS)}, found {sorted(changed)}")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        shutil.copy2(JOBS, JOBS.with_name(f"jobs.pre-foundry-{stamp}.json"))
        tmp = JOBS.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        os.replace(tmp, JOBS)
    print(json.dumps({"updated": changed, "provider": "foundry-qwen35b", "model": MODEL, "installed": installed}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
