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
    return json.loads(MANIFEST.read_text())


def test_repository_contract_is_structurally_valid():
    assert contracts.validate_data(ROOT, load()) == []


def test_cli_check_passes():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "check_certificate_contracts.py")],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


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


def _forbidding_the_bound_text(field):
    """A manifest copy whose first binding forbids (in `field`) the very text it
    binds, which is certainly present in the bound file."""
    data = copy.deepcopy(load())
    binding = data["claims"][0]["publication_bindings"][0]
    binding.pop("must_not_contain", None)
    binding.pop("overclaim_guards", None)
    binding[field] = [binding["contains"]]
    return data


def test_retracted_text_in_the_publication_fails():
    errors = contracts.validate_data(ROOT, _forbidding_the_bound_text("must_not_contain"))
    assert any("quarantined/stale text is present" in error for error in errors)


def test_overclaim_guard_text_in_the_publication_fails_with_its_own_message():
    errors = contracts.validate_data(ROOT, _forbidding_the_bound_text("overclaim_guards"))
    assert any("overclaim-guard text is present" in error for error in errors)
    assert not any("quarantined/stale" in error for error in errors)


def test_forbidden_text_lists_must_be_string_lists():
    for field in ("must_not_contain", "overclaim_guards"):
        data = copy.deepcopy(load())
        data["claims"][0]["publication_bindings"][0][field] = "not a list"
        errors = contracts.validate_data(ROOT, data)
        assert any(f"{field} must be a string list" in error for error in errors), field


def test_text_is_either_a_retraction_or_a_guard_not_both():
    data = copy.deepcopy(load())
    binding = data["claims"][0]["publication_bindings"][0]
    binding["must_not_contain"] = ["zz never published zz"]
    binding["overclaim_guards"] = ["zz never published zz"]
    errors = contracts.validate_data(ROOT, data)
    assert any("both as a retraction and as an overclaim guard" in error for error in errors)
