#!/usr/bin/env python3
"""Validate and replay claim-bound certificate contracts.

Unlike filename discovery, this gate starts from an explicit public claim and
binds it to exact artifact bytes, publication text, a replay command, semantic
success output, and a failure control.  A path string by itself is not evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "certificates" / "contracts.json"
DIRECTORY_CLASSES = {
    "certified_local", "partial_local", "research_fence",
    "formal_external", "reference_only",
}
REPLAY_PROFILES = {"fast", "slow"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_data(root: Path, data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "efa-certificate-contracts-v1":
        errors.append("schema must be efa-certificate-contracts-v1")

    inventory = data.get("directories")
    if not isinstance(inventory, list):
        return errors + ["directories must be a list"]
    listed = []
    for i, item in enumerate(inventory):
        where = f"directories[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            continue
        path = item.get("path")
        listed.append(path)
        if not isinstance(path, str) or not path.startswith("certificates/"):
            errors.append(f"{where}.path must name a certificate directory")
        elif not (root / path).is_dir():
            errors.append(f"{where}.path does not exist: {path}")
        if item.get("classification") not in DIRECTORY_CLASSES:
            errors.append(f"{where}.classification is invalid")
        if not isinstance(item.get("boundary"), str) or not item["boundary"].strip():
            errors.append(f"{where}.boundary must be non-empty")
    actual = sorted(
        str(p.relative_to(root))
        for p in (root / "certificates").iterdir()
        if p.is_dir()
    )
    if sorted(x for x in listed if isinstance(x, str)) != actual:
        missing = sorted(set(actual) - set(listed))
        extra = sorted(set(listed) - set(actual))
        errors.append(f"directory inventory mismatch; missing={missing}, extra={extra}")
    if len(listed) != len(set(listed)):
        errors.append("directory inventory contains duplicates")

    claims = data.get("claims")
    if not isinstance(claims, list):
        return errors + ["claims must be a list"]
    ids = [c.get("id") for c in claims if isinstance(c, dict)]
    if len(ids) != len(set(ids)):
        errors.append("claim ids must be unique")
    for i, claim in enumerate(claims):
        where = f"claims[{i}]"
        if not isinstance(claim, dict):
            errors.append(f"{where} must be an object")
            continue
        for key in ("id", "statement", "scope"):
            if not isinstance(claim.get(key), str) or not claim[key].strip():
                errors.append(f"{where}.{key} must be non-empty")
        if claim.get("status") not in {"promoted", "partial", "retracted"}:
            errors.append(f"{where}.status is invalid")
        machine_verdict = claim.get("machine_verdict")
        if claim.get("status") == "promoted" and (
                not isinstance(machine_verdict, str) or not machine_verdict.strip()):
            errors.append(f"{where}: promoted claim needs a machine_verdict")

        bindings = claim.get("publication_bindings", [])
        if claim.get("status") == "promoted" and not bindings:
            errors.append(f"{where}: promoted claim needs a publication binding")
        for j, binding in enumerate(bindings):
            bwhere = f"{where}.publication_bindings[{j}]"
            path = root / str(binding.get("path", ""))
            needle = binding.get("contains")
            if not path.is_file():
                errors.append(f"{bwhere}.path does not exist")
            elif not isinstance(needle, str) or needle not in path.read_text(errors="replace"):
                errors.append(f"{bwhere}: bound text is absent from {binding.get('path')}")
            if path.is_file():
                text = path.read_text(errors="replace")
                forbidden = binding.get("must_not_contain", [])
                if not isinstance(forbidden, list) or not all(
                        isinstance(x, str) and x for x in forbidden):
                    errors.append(f"{bwhere}.must_not_contain must be a string list")
                else:
                    for stale in forbidden:
                        if stale in text:
                            errors.append(
                                f"{bwhere}: quarantined/stale text is present: {stale!r}")

        artifacts = claim.get("artifacts", [])
        if claim.get("status") == "promoted" and not artifacts:
            errors.append(f"{where}: promoted claim needs hashed artifacts")
        for j, artifact in enumerate(artifacts):
            awhere = f"{where}.artifacts[{j}]"
            rel = artifact.get("path", "")
            path = root / str(rel)
            digest = artifact.get("sha256")
            if not path.is_file():
                errors.append(f"{awhere}.path does not exist: {rel}")
            elif digest != sha256(path):
                errors.append(f"{awhere}: sha256 mismatch for {rel}")

        replays = claim.get("replays", [])
        if claim.get("status") == "promoted" and not any(
                r.get("certifies_claim") is True for r in replays if isinstance(r, dict)):
            errors.append(f"{where}: promoted claim needs a claim-certifying replay")
        for j, replay in enumerate(replays):
            rwhere = f"{where}.replays[{j}]"
            if replay.get("profile") not in REPLAY_PROFILES:
                errors.append(f"{rwhere}.profile is invalid")
            argv = replay.get("argv")
            if not isinstance(argv, list) or not argv or not all(
                    isinstance(x, str) and x for x in argv):
                errors.append(f"{rwhere}.argv must be a non-empty string list")
            entrypoint = replay.get("entrypoint")
            hashed_paths = {a.get("path") for a in artifacts if isinstance(a, dict)}
            if not isinstance(entrypoint, str) or entrypoint not in hashed_paths:
                errors.append(f"{rwhere}.entrypoint must be a hashed claim artifact")
            if isinstance(argv, list) and (
                    len(argv) < 3 or argv[:2] != ["python3", "-I"] or argv[2] != entrypoint):
                errors.append(
                    f"{rwhere}.argv must execute the hashed entrypoint as python3 -I <entrypoint>")
            expected = replay.get("stdout_contains")
            if not isinstance(expected, list) or not expected or not all(
                    isinstance(x, str) and x for x in expected):
                errors.append(f"{rwhere}.stdout_contains must be a non-empty string list")
            elif replay.get("certifies_claim") is True and machine_verdict not in expected:
                errors.append(
                    f"{rwhere}: certifying replay must require the exact machine_verdict")
            if not isinstance(replay.get("timeout_seconds"), int) or replay["timeout_seconds"] < 1:
                errors.append(f"{rwhere}.timeout_seconds must be a positive integer")
            control = replay.get("failure_control")
            if not isinstance(control, dict) or control.get("kind") not in {
                    "embedded", "external", "none_explained"}:
                errors.append(f"{rwhere}.failure_control must state the planted-failure boundary")
            elif not isinstance(control.get("evidence"), str) or not control["evidence"].strip():
                errors.append(f"{rwhere}.failure_control.evidence must be non-empty")
    return errors


def copy_repo(root: Path, destination: Path) -> None:
    shutil.copytree(
        root, destination, dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"),
    )


def tree_hashes(root: Path) -> dict[str, str]:
    """Snapshot replay-visible files so a checker cannot rewrite its own evidence."""
    out = {}
    for path in root.rglob("*"):
        if not path.is_file() or any(
                part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        out[str(path.relative_to(root))] = sha256(path)
    return out


def run_replays(root: Path, data: dict, profile: str, claim_id: str | None) -> list[str]:
    failures: list[str] = []
    selected = []
    for claim in data["claims"]:
        if claim_id and claim["id"] != claim_id:
            continue
        for replay in claim.get("replays", []):
            if replay["profile"] == profile:
                selected.append((claim, replay))
    if claim_id and not any(c["id"] == claim_id for c in data["claims"]):
        return [f"unknown claim id: {claim_id}"]
    if not selected:
        return [f"no {profile} replays selected"]

    with tempfile.TemporaryDirectory(prefix="efa-contract-") as td:
        sandbox = Path(td) / "repo"
        copy_repo(root, sandbox)
        for claim, replay in selected:
            before = tree_hashes(sandbox)
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            try:
                proc = subprocess.run(
                    replay["argv"], cwd=sandbox, env=env,
                    capture_output=True, text=True,
                    timeout=replay["timeout_seconds"],
                )
            except subprocess.TimeoutExpired:
                failures.append(f"{claim['id']}: replay timed out")
                continue
            output = proc.stdout + proc.stderr
            if proc.returncode != replay.get("exit_code", 0):
                failures.append(f"{claim['id']}: exit {proc.returncode}; output={output[-800:]}")
            for needle in replay["stdout_contains"]:
                if needle not in output:
                    failures.append(f"{claim['id']}: missing semantic output {needle!r}")
            for needle in replay.get("stdout_not_contains", []):
                if needle in output:
                    failures.append(f"{claim['id']}: forbidden output present {needle!r}")
            after = tree_hashes(sandbox)
            if after != before:
                changed = sorted(set(before) | set(after))
                changed = [path for path in changed if before.get(path) != after.get(path)]
                failures.append(
                    f"{claim['id']}: replay mutated its sandbox: {changed[:8]}")
            print(f"contract replay {claim['id']}: {'PASS' if not any(x.startswith(claim['id'] + ':') for x in failures) else 'FAIL'}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--profile", choices=sorted(REPLAY_PROFILES))
    parser.add_argument("--claim")
    args = parser.parse_args()
    manifest = args.manifest.resolve()
    root = manifest.parent.parent if manifest.name == "contracts.json" else ROOT
    try:
        data = json.loads(manifest.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"certificate-contracts: cannot load manifest: {exc}", file=sys.stderr)
        return 2
    errors = validate_data(root, data)
    if errors:
        print("certificate-contracts FAILED:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"certificate-contracts: {len(data['directories'])} directories inventoried; {len(data['claims'])} claims bound")
    if args.profile:
        errors = run_replays(root, data, args.profile, args.claim)
        if errors:
            print("certificate-contracts replay FAILED:")
            for error in errors:
                print(f"  - {error}")
            return 1
    print("certificate-contracts OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
