"""Keep the 2026-09-27 gap-map curation tied to its offline re-checks."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
CHECKS = ROOT / "experiments" / "claude-freshness-20260927" / "curation_checks.py"


def load_checks():
    spec = importlib.util.spec_from_file_location("curation_checks", CHECKS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rows(problem):
    gm = json.loads((ROOT / "atlas" / "gap_map.json").read_text(encoding="utf-8"))
    return [e for e in gm["entries"] if e["problem"] == problem]


def test_curation_checks_pass():
    result = subprocess.run([sys.executable, "-I", "-B", str(CHECKS)], cwd=ROOT,
                            text=True, capture_output=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "[FAIL]" not in result.stdout
    assert "all curation checks passed" in result.stdout


def test_closed_rows_carry_the_rechecked_values():
    mod = load_checks()
    (r376,) = rows(376)
    assert r376["status"] == "closed"
    assert r376["lower"]["value"] == r376["upper"]["value"] == str(mod.A030979_1375)
    (r1005,) = rows(1005)
    assert r1005["status"] == "closed"
    assert r1005["lower"]["value"] == r1005["upper"]["value"] == "27"
    assert mod.mayer_erdos(101) == 27


def test_repointed_rows_match_the_checks():
    mod = load_checks()
    (r156,) = rows(156)
    top9 = max(hi for S, lo, hi in mod.SIDON_WITNESSES if len(S) == 9)
    assert r156["quantity"].startswith("i(9)")
    assert int(r156["lower"]["value"]) == top9
    witness = tuple(int(x) for x in
                    r156["lower"]["source"].split("{")[1].split("}")[0].split(","))
    assert mod.is_maximal_sidon(witness, top9)
    (r1095,) = rows(1095)
    assert r1095["quantity"].startswith("A003458(401)") and max(mod.G) == 400
    (r20,) = rows(20)
    assert r20["lower"]["value"] == "40" and len(set(mod.f39())) == 39
    (r302,) = rows(302)
    assert r302["quantity"].startswith("A390395(735)")
    assert (r302["lower"]["value"], r302["upper"]["value"]) == ("608", "609")


def test_curated_rows_stay_literature_grade():
    # no certificate backs these rows, so the computed class must stay C3
    for p in (20, 156, 302, 376, 451, 1005, 1057, 1062, 1095):
        for e in rows(p):
            assert e["confidence"] == "C3", p
