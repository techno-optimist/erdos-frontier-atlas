"""Claim-bound certificate contract tests."""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "certificates" / "contracts.json"

spec = importlib.util.spec_from_file_location(
    "check_certificate_contracts", ROOT / "tools" / "check_certificate_contracts.py")
contracts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contracts)


def load():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_repository_contract_is_structurally_valid():
    assert contracts.validate_data(ROOT, load()) == []


def test_cli_check_passes():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_certificate_contracts.py")],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_python_replay_uses_current_interpreter():
    argv = contracts.replay_argv(["python3", "-I", "certificate.py"])
    assert argv == [sys.executable, "-X", "utf8", "-I", "certificate.py"]


def test_nonexistent_artifact_cannot_count_as_evidence():
    data = copy.deepcopy(load())
    data["claims"][0]["artifacts"][0]["path"] = "certificates/does-not-exist.json"
    errors = contracts.validate_data(ROOT, data)
    assert any("does not exist" in error for error in errors)


def test_artifact_bytes_are_bound_not_just_paths():
    data = copy.deepcopy(load())
    data["claims"][0]["artifacts"][0]["sha256"] = "0" * 64
    errors = contracts.validate_data(ROOT, data)
    assert any("sha256 mismatch" in error for error in errors)


def test_publication_claim_must_still_exist_verbatim():
    data = copy.deepcopy(load())
    data["claims"][0]["publication_bindings"][0]["contains"] = "fabricated claim"
    errors = contracts.validate_data(ROOT, data)
    assert any("bound text is absent" in error for error in errors)


def test_new_certificate_directory_cannot_bypass_inventory(tmp_path):
    # The current inventory is exact; adding a directory without a classification
    # must fail before it can be silently swept up by filename discovery.
    root = tmp_path / "repo"
    (root / "certificates").mkdir(parents=True)
    for item in load()["directories"]:
        (root / item["path"]).mkdir(parents=True)
    (root / "certificates" / "unclassified-new-lane").mkdir()
    errors = contracts.validate_data(root, load())
    assert any("directory inventory mismatch" in error for error in errors)
