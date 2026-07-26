"""The CI workflow must be able to reach the checks it claims to run.

This repository's whole subject is gates that cannot fail. On 2026-07-25 it
shipped one of its own: `.github/workflows/verify.yml`, the repo's first CI, and
it was reported as green. It had failed **8 for 8** since the day it was added —
on `main` and on every pull request — dying after ~10 seconds inside
`actions/setup-python`, because `cache: pip` looks for `requirements.txt` or
`pyproject.toml` and this repo pins `requirements-dev.lock`. `make audit-fast`
never executed once. The red X read, at a glance, exactly like the green tick.

Fixing that surfaced two more failures immediately: `pytest` was never in the
lock file, so `make test` could not run on a clean machine; and the contracts
gate then caught that editing the lock file broke a pinned artifact hash.

Three failures, all of them in the *plumbing* rather than the mathematics, and
none of them visible from reading the YAML. So these tests check the plumbing:
every path the workflow names must exist, every `make` target it invokes must be
defined, and every module those targets need must be installable from the lock
file we actually ship.

What this CANNOT check is whether the workflow *ran* — that lives on GitHub, not
in the tree. The discipline for that is unchanged and belongs to the author:
watch a gate FAIL on a deliberate break, then PASS. A gate observed only in the
passing state is unproven. Read the run duration, not the check name — a job
that "fails" in four seconds never ran your checks.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "verify.yml"


def _text():
    return WORKFLOW.read_text(encoding="utf-8")


def test_workflow_exists():
    assert WORKFLOW.exists(), "the repo's CI workflow is missing"


def test_pip_cache_has_a_dependency_path_that_exists():
    """The exact defect that made this workflow a no-op for a full day.

    `actions/setup-python` with `cache: pip` and no `cache-dependency-path`
    searches for `requirements.txt`/`pyproject.toml`. We ship neither, so the
    step errors and the job dies before running anything.
    """
    text = _text()
    if "cache: pip" not in text:
        return
    n_cache = text.count("cache: pip")
    paths = re.findall(r"cache-dependency-path:\s*(\S+)", text)
    assert len(paths) == n_cache, (
        f"{n_cache} setup-python step(s) use `cache: pip` but only {len(paths)} "
        f"declare `cache-dependency-path`. Without it the action looks for "
        f"requirements.txt/pyproject.toml, finds neither, and the job dies in "
        f"setup — which is how this workflow failed 8 times in a row while "
        f"looking like it was configured correctly."
    )
    for p in paths:
        assert (ROOT / p).exists(), f"cache-dependency-path points at a missing file: {p}"


def test_every_installed_requirements_file_exists():
    for req in re.findall(r"pip install -r (\S+)", _text()):
        assert (ROOT / req).exists(), f"workflow installs from a missing file: {req}"


def test_every_make_target_the_workflow_runs_is_defined():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    defined = set(re.findall(r"^([A-Za-z0-9_.-]+):", makefile, re.M))
    for target in re.findall(r"^\s*- run: make (\S+)", _text(), re.M):
        assert target in defined, (
            f"workflow runs `make {target}` but the Makefile defines no such "
            f"target; the job would fail in CI only"
        )


def test_lockfile_provides_the_tools_the_audit_targets_invoke():
    """`make audit-fast` shells out to pytest. A clean runner installs only the
    lock file, so anything the audit invokes has to be pinned there."""
    lock = (ROOT / "requirements-dev.lock").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    if "pytest" in makefile:
        assert re.search(r"^pytest[=<>~]", lock, re.M), (
            "the Makefile invokes pytest but requirements-dev.lock does not pin "
            "it, so `make audit-fast` cannot run on a clean checkout — it failed "
            "in CI with 'No module named pytest' for exactly this reason"
        )


def test_lockfile_is_pinned_not_floating():
    """A floating dependency silently changes what a replay means."""
    lock = (ROOT / "requirements-dev.lock").read_text(encoding="utf-8")
    for line in lock.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        assert "==" in line, f"unpinned dependency in the lock file: {line!r}"
