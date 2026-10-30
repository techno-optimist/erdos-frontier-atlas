"""The Plasma AI overlay must never be able to promote an external standing
into a status (CLAUDE.md rule 1), and every record must carry its CC BY 4.0
attribution."""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _doc():
    return json.loads((ROOT / "atlas" / "plasma_claims.json").read_text(encoding="utf-8"))


def test_overlay_validates():
    p = subprocess.run([sys.executable, "tools/validate_plasma_claims.py"],
                       cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr


def test_no_entry_changed_a_status():
    offenders = [e["erdos_id"] for e in _doc()["entries"]
                 if e.get("status_changed_by_this_entry") is not False]
    assert not offenders


def test_every_record_credits_plasma_cc_by():
    for e in _doc()["entries"]:
        assert e["source"]["license"] == "CC-BY-4.0", e["erdos_id"]
        assert e["source"]["attribution"] == "Plasma AI, github.com/plasma-ai/erdos, CC BY 4.0"


def test_notice_credits_plasma():
    assert "plasma-ai/erdos" in (ROOT / "NOTICE").read_text(encoding="utf-8")
