"""Unit tests for the GENERIC crater engine (tools/craterlib/).

tests/test_jc_crater.py pins the JC crater's behaviour byte for byte; this file
pins the generalization: both polarities, the index-semantics alias table, and
the planted-failure controls that prove each gate can still fail.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import craterlib  # noqa: E402
from craterlib import selftest  # noqa: E402


def test_selftest_controls_all_pass():
    """Every control in craterlib.selftest, including the planted failures."""
    passed, failed, skipped = selftest.run(verbose=False)
    assert failed == 0
    assert passed >= 25


def test_selftest_cli_exits_zero():
    proc = subprocess.run([sys.executable, str(ROOT / "tools" / "crater.py"),
                           "selftest", "--quiet"], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "0 failed" in proc.stdout


def test_polarity_is_exactly_the_licensed_pair_function():
    """The whole refuted/proved difference: which ordered pairs an `implies`
    edge licenses. Everything else in the fixpoint is shared."""
    jc = craterlib.load_config(ROOT / "atlas" / "jc-crater" / "crater.json", root=ROOT)
    e = {"from": "x", "to": "y", "type": "implies"}
    assert craterlib.licensed_pairs(jc, e) == [("y", "x")]      # modus tollens
    jc.polarity = "proved"
    assert craterlib.licensed_pairs(jc, e) == [("x", "y")]      # modus ponens
    jc.polarity = "refuted"
    assert craterlib.licensed_pairs(jc, {"from": "x", "to": "y", "type": "equivalent"}) \
        == [("x", "y"), ("y", "x")]


def test_jc_wrapper_and_generic_cli_agree():
    """tools/validate_jc_crater.py is a thin wrapper: same stdout as the
    generic entry point, to the byte."""
    a = subprocess.run([sys.executable, str(ROOT / "tools" / "validate_jc_crater.py")],
                       capture_output=True, text=True)
    b = subprocess.run([sys.executable, str(ROOT / "tools" / "validate_crater.py"),
                        "jc-crater"], capture_output=True, text=True)
    assert a.returncode == 0 and b.returncode == 0, a.stdout + b.stdout
    assert a.stdout == b.stdout


def test_jc_config_declares_a_licensed_reach():
    """The one part of REFUTED_ALL_N_GE_3 that is a mathematical claim -- the
    reach "all n >= 3" -- must name the artifact that licenses it."""
    jc = craterlib.load_config(ROOT / "atlas" / "jc-crater" / "crater.json", root=ROOT)
    lic = jc.level(jc.full).reach_license
    assert lic == "atlas/jc-crater/padding_check.py"
    assert (ROOT / lic).exists()


def test_config_rejects_a_full_level_that_cannot_outrank_the_floor():
    from craterlib.scaffold import default_config
    cfg = default_config("bad", "refuted")
    cfg["levels"][0]["rank"] = 0
    with pytest.raises(craterlib.ConfigError):
        craterlib.CraterSpec(cfg, ROOT, ROOT / "atlas" / "bad")


def test_config_rejects_an_excluded_level_that_is_also_rendered():
    from craterlib.scaffold import default_config
    cfg = default_config("bad", "refuted")
    cfg["excluded_level"] = "OPEN"
    with pytest.raises(craterlib.ConfigError):
        craterlib.CraterSpec(cfg, ROOT, ROOT / "atlas" / "bad")


# -- `crater.py list` degrades per row ---------------------------------------

def _crater_cli():
    """Load tools/crater.py as a module so ATLAS/ROOT can be repointed."""
    spec = importlib.util.spec_from_file_location(
        "crater_cli_under_test", ROOT / "tools" / "crater.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _atlas_with(tmp_path, good=(), broken=(), halfwritten=()):
    """Build a scratch atlas/ containing well-formed and malformed craters.

    `broken`     -- crater.json is not even parseable JSON
    `halfwritten` -- valid crater.json, implication_graph.json not written yet
                     (the normal race when several agents share this branch)
    """
    from craterlib.scaffold import new_crater
    atlas = tmp_path / "atlas"
    atlas.mkdir()
    for slug in good:
        new_crater(tmp_path, slug, "refuted")
    for slug in broken:
        (atlas / slug).mkdir()
        (atlas / slug / "crater.json").write_text('{"schema": "efa-crater-')
    for slug in halfwritten:
        new_crater(tmp_path, slug, "refuted")
        (atlas / slug / "implication_graph.json").unlink()
    return atlas


def test_list_survives_a_malformed_crater_dir(tmp_path, capsys):
    """ONE broken crater must cost one ROW, not the whole listing and never a
    raw traceback -- half-scaffolded dirs are normal on a shared branch."""
    mod = _crater_cli()
    mod.ROOT = tmp_path
    mod.ATLAS = _atlas_with(tmp_path, good=["aaa-good", "zzz-good"],
                            broken=["mmm-broken"], halfwritten=["nnn-half"])
    rc = mod.cmd_list([])
    out = capsys.readouterr().out
    assert rc == 0, out                      # not every crater failed
    assert "Traceback" not in out
    # the good rows still printed, including the one sorted AFTER both failures
    assert "aaa-good" in out and "zzz-good" in out
    assert "2 nodes, 0 edges" not in out     # scaffold is 1 node, 0 edges
    for line in out.splitlines():
        if line.startswith("zzz-good"):
            assert "1 nodes, 0 edges" in line
    # ...and each failure is one clear, short, slug-tagged line
    for slug in ("mmm-broken", "nnn-half"):
        line = next(ln for ln in out.splitlines() if ln.startswith(slug))
        assert "ERROR" in line and len(line) < 200, line
    assert "2 of 4 crater(s) could not be read." in out


def test_list_exits_nonzero_only_when_every_crater_failed(tmp_path, capsys):
    mod = _crater_cli()
    mod.ROOT = tmp_path
    mod.ATLAS = _atlas_with(tmp_path, broken=["a-broken"], halfwritten=["b-half"])
    assert mod.cmd_list([]) == 1
    assert "Traceback" not in capsys.readouterr().out


def test_list_on_an_empty_atlas_is_not_a_failure(tmp_path, capsys):
    mod = _crater_cli()
    mod.ROOT = tmp_path
    mod.ATLAS = _atlas_with(tmp_path)
    assert mod.cmd_list([]) == 0
    assert "no craters found" in capsys.readouterr().out


# -- the one machine-checkable slice of edge mis-typing -----------------------

def test_same_ordered_pair_may_not_disagree_on_index_semantics():
    """engine.py is explicit that a mis-typed edge WILL launder FLOOR into FULL
    and cannot be detected. The single exception a machine CAN see: the same
    ordered pair declared both ways is self-contradictory."""
    from craterlib import selftest as st
    names = {c.__name__ for c in st.CASES}
    assert "planted_same_ordered_pair_disagreeing_on_semantics_fails" in names
    assert "opposite_direction_edges_may_disagree_on_semantics" in names


def test_engine_docstring_does_not_claim_full_is_root_only():
    """Regression on the overclaim itself: the corollary asserting 'FULL
    originates only from a root' was false and is not to come back."""
    from craterlib import engine
    doc = engine.__doc__
    assert "FULL originates only from a root" not in doc
    assert "FLOOR never becomes FULL" not in doc
    assert "WITNESS_SPEC.md section D.3" in doc
    assert "mis-typed edge WILL launder" in doc
