"""atlas/tools.json and atlas/ai_results.json must validate, never move a
status, and keep status-implying words out of our own wording."""
import importlib.util, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent

def _load():
    spec = importlib.util.spec_from_file_location("validate_tools", ROOT / "tools" / "validate_tools.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def test_tools_and_results_validate():
    p = subprocess.run([sys.executable, "tools/validate_tools.py"], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr

def test_results_never_move_status_and_ai_role_is_labelled():
    d = json.loads((ROOT / "atlas" / "ai_results.json").read_text(encoding="utf-8"))
    for e in d["entries"]:
        assert e["status_changed_by_this_entry"] is False
        assert e["attribution"] in ("reported", "claimed")
        assert e["ai_involvement"]["status"] in ("confirmed", "unconfirmed")

def test_banned_words_caught_outside_urls():
    m = _load()
    assert m.BANNED.search("this was solved")
    assert m.BANNED.search("a new record")
    assert not m.BANNED.search("a reported bound")
    flagged = [p for p, s in m.strings({"u": "https://zenodo.org/records/1", "n": "fine"})
               if not s.startswith("https://") and m.BANNED.search(s)]
    assert flagged == []

def test_unvetted_entries_are_claims_and_counted():
    d = json.loads((ROOT / "atlas" / "ai_results.json").read_text(encoding="utf-8"))
    unvetted = [e for e in d["entries"] if e.get("vetting") == "unvetted"]
    assert d["counts"]["unvetted"] == len(unvetted)
    for e in unvetted:
        assert e["attribution"] == "claimed"
        assert "unvetted" in e.get("note", "").lower()
    m = _load()
    bad = dict(d, entries=[dict(unvetted[0], attribution="reported")] if unvetted else [])
    assert any("must be attributed 'claimed'" in x for x in m.results_counts(bad)) or not unvetted
