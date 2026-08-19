#!/usr/bin/env python3
"""Portable exact replay for the fifteen-state Hamiltonian-chain extension."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
AUDIT = HERE / "audit"
PACKAGE = HERE.parent
M14 = PACKAGE / "homogeneous-partial-fourteen-state-wall" / "source"
SIX = PACKAGE / "homogeneous-partial-six-state-extension" / "source"
SIX_AUDIT = PACKAGE / "homogeneous-partial-six-state-extension" / "audit"
FIVE = PACKAGE / "homogeneous-partial-five-state-wall" / "source"

EXPECTED = {
    SOURCE: {
        "FIFTEEN_STATE_CHAIN_CLOSURE.md": "e9ac7b84d22143f985701cf9f1f65b0e82d072e601fa958a2d5de0bdc0f5072b",
        "probe_chain_product.cpp": "1deb314663a65c0a4536334676b3f2826d6602bd53daa57a2d7eb18df3a5101b",
        "run.ps1": "a3f14e5a7870caacb509ef0d61fd1b9eb114533b2aa232a85839866ee63c1ae8",
        "run.sh": "e86e1045c477fa5d8ce4c9fcdf3b3998b05f7ea7d8aad882af89b83b7ba70355",
        "SHA256SUMS": "f502b1ed111160e81d3bb7dcead77de113817a94c69a31d6e001862f23af5e75",
        "verify_chain_residual.py": "893197d0c841113bea7eeb8619274953db485092f25d33980ebe56a65efb8149",
    },
    AUDIT: {
        "HOSTILE_AUDIT.md": "59b6c19ef11f0260ea0e82b0f2ad5406fccac754378163997db837c7caadaf9b",
        "hostile_fifteen_audit.py": "f7405a10c1f586b42fa2a9d6ae5a620b7caacc34be81568ed7749b9c9fc37bc9",
        "run.ps1": "c270176a698bd0338a178553c94eeada0455dfdd173632d001ad11e5eb5d347f",
        "run.sh": "66fd5bc4688a671be7c18caeb734b62ea8f04d9d7ae3c55c700521d3e321a27d",
        "SHA256SUMS": "4a2a0cc109c33bee10e01990c8238439aa07882823b01eadb717e2631fcdaefe",
    },
}


class UsageError(Exception):
    pass


def need(condition: bool, note: str) -> None:
    if not condition:
        raise AssertionError(note)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_no_args(argv: list[str]) -> None:
    if argv:
        raise UsageError("this verifier accepts no arguments")


def frozen_snapshot() -> dict[str, str]:
    result: dict[str, str] = {}
    for directory, expected in EXPECTED.items():
        names = {path.name for path in directory.iterdir() if path.is_file()}
        need(names == set(expected), f"frozen file census: {directory.name}")
        for name, expected_hash in expected.items():
            actual = digest(directory / name)
            need(actual == expected_hash, f"frozen hash: {directory.name}/{name}")
            result[str(directory / name)] = actual
    for path in (
        M14 / "SHA256SUMS",
        SIX / "SHA256SUMS",
        FIVE / "SHA256SUMS",
        SIX_AUDIT / "independent_six_scope_physical.py",
    ):
        result[str(path)] = digest(path)
    return result


def run_checked(
    argv: tuple[str, ...], marker: str | None, cwd: Path = HERE
) -> str:
    completed = subprocess.run(
        argv,
        cwd=cwd,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise AssertionError(
            f"sub-replay failed ({completed.returncode}): {argv}\n{output[-3000:]}")
    if marker is not None:
        need(marker in output, f"missing sub-replay marker: {marker}")
    return output


def product_replay(compiler: str) -> str:
    with tempfile.TemporaryDirectory(prefix="q42-fifteen-state-") as name:
        binary = Path(name) / (
            "fifteen-product.exe" if os.name == "nt" else "fifteen-product")
        run_checked((
            compiler,
            "-std=c++17",
            "-O3",
            "-Wall",
            "-Wextra",
            "-pedantic",
            str(SOURCE / "probe_chain_product.cpp"),
            "-o",
            str(binary),
        ), marker=None, cwd=SOURCE)
        return run_checked(
            (str(binary), "all-critical"),
            "PASS_EXACT_FIFTEEN_CHAIN_CRITICAL_PRODUCT_SCREEN",
            cwd=SOURCE,
        )


def main(argv: list[str]) -> None:
    require_no_args(argv)
    try:
        require_no_args(["--planted-invalid-argument"])
    except UsageError:
        pass
    else:
        raise AssertionError("planted invalid argument was accepted")

    before = frozen_snapshot()
    compiler = shutil.which("g++")
    need(compiler is not None, "g++ is required for the fifteen-state replay")
    runs = (
        (
            (sys.executable, "-I", str(SOURCE / "verify_chain_residual.py")),
            "PASS_EXACT_FIFTEEN_CHAIN_RESIDUAL_CLOSURE",
        ),
        (
            (sys.executable, "-I", str(AUDIT / "hostile_fifteen_audit.py"),
             "--source", str(SOURCE), "--m14", str(M14), "--six", str(SIX),
             "--five", str(FIVE), "--physical-auditor",
             str(SIX_AUDIT / "independent_six_scope_physical.py")),
            "APPROVE_Q42_PARTIAL_FIFTEEN_CHAIN_CLOSURE",
        ),
    )
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = tuple(
            executor.submit(run_checked, command, marker)
            for command, marker in runs
        )
        product_future = executor.submit(product_replay, compiler)
        source_output, audit_output = (future.result() for future in futures)
        product_output = product_future.result()

    for output in (source_output, product_output, audit_output):
        print(output, end="" if output.endswith("\n") else "\n")

    for marker in (
        "FIFTEEN_SPECTRAL_PARTITION partial_support_below_if_at_most=14 q2_controls=20580 q1_high_controls=195 critical_maps=16",
        "FIFTEEN_EXPLICIT_PRODUCTS pairs=3600 max_horizon=19",
    ):
        need(marker in source_output, f"missing source semantic marker: {marker}")
    need(
        "FIFTEEN_CHAIN_CRITICAL tables=16 pairs=3600 missing=0 max_horizon=18 max_reached=65107 reached_sum=920075"
        in product_output,
        "missing independent product census",
    )
    for marker in (
        "PASS_TOTAL_RED_AND_COLLATZ_PARTITION 20580 195 critical 16",
        "PASS_ALL_LABELED_WORDS_AND_PHYSICAL_LIFTS pairs 3600 lifts 25200 unit_columns 26775",
        "PASS_LIVE_TRIM_COMBINED_AT_MOST_FIFTEEN_SCOPE",
    ):
        need(marker in audit_output, f"missing hostile semantic marker: {marker}")

    need(frozen_snapshot() == before, "replay mutated frozen fifteen-state bytes")
    print("PLANTED_BAD_ARG_REJECTED")
    print("FIFTEEN_STATE_SOURCE_AUDIT_AND_DEPENDENCIES_NONMUTATION_OK")
    print("PASS_PORTABLE_AT_MOST_FIFTEEN_STATE_CHAIN_EXTENSION")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except UsageError as exc:
        print(f"usage error: {exc}", file=sys.stderr)
        raise SystemExit(2)
