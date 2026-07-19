"""Cartography of Numbers (book/BOOK.md): living-book contract tests.

Mirrors tests/test_state_of_frontier.py: the build is deterministic, the
committed edition is current, and the staleness gate actually fires when the
underlying data moves.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "build_book", ROOT / "book" / "build_book.py")
bb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bb)

BANNER = ("SEED EDITION — this book accretes as the frontier moves; it\n"
          "> circulates externally only after the EFA-DR1 DOI is live and the first\n"
          "> observatory note exists.")

# Every input the generator reads; the tmp-copy test replicates exactly these.
BOOK_INPUTS = [
    "atlas/gap_map.json",
    "atlas/effectivization_shortlist.json",
    "certificates/erdos-13/table.json",
    "observatory/measurements.json",
    "README.md",
]


def test_deterministic():
    """Two builds from the same data are byte-identical (no timestamps)."""
    assert bb.Book(ROOT).generate() == bb.Book(ROOT).generate()


def test_committed_book_is_current():
    """book/BOOK.md must match a regeneration from the data."""
    p = subprocess.run(
        [sys.executable, str(ROOT / "book" / "build_book.py"), "--check"],
        capture_output=True, text=True)
    assert p.returncode == 0, f"stale book:\n{p.stdout}\n{p.stderr}"


def test_check_fails_after_data_mutation(tmp_path):
    """The staleness gate fires when a ledger changes under the committed book."""
    for rel in BOOK_INPUTS:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, dst)
    shutil.copytree(ROOT / "book", tmp_path / "book")

    cmd = [sys.executable, str(tmp_path / "book" / "build_book.py"),
           "--check", "--root", str(tmp_path)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 0, f"pristine copy should check clean:\n{p.stdout}\n{p.stderr}"

    gm_path = tmp_path / "atlas" / "gap_map.json"
    gm = json.loads(gm_path.read_text())
    del gm["entries"][0]                       # the frontier "moves"
    gm_path.write_text(json.dumps(gm))

    p = subprocess.run(cmd, capture_output=True, text=True)
    assert p.returncode == 1, "check must fail after a data mutation"
    assert "STALE" in p.stdout


def test_status_banner_opens_the_book():
    """Hard rule: the seed-edition status banner is the first visible content."""
    book = bb.Book(ROOT).generate()
    first_visible = book.split("-->", 1)[1].lstrip()   # skip the generated-file comment
    assert first_visible.startswith("> **STATUS: SEED EDITION")
    assert BANNER in book


def test_all_six_chapters_present():
    chapters = sorted((ROOT / "book" / "chapters").glob("*.md"))
    assert [c.name for c in chapters] == [
        "00-preface.md", "01-the-map.md", "02-fences.md",
        "03-the-observatory.md", "04-walls.md", "05-methods.md"]
    book = bb.Book(ROOT).generate()
    for heading in ("# Cartography of Numbers", "# 1 · The Map", "# 2 · Fences",
                    "# 3 · The Observatory", "# 4 · Walls",
                    "# 5 · Methods — the field's instruments"):
        assert heading in book


def test_no_unexpanded_directives():
    book = bb.Book(ROOT).generate()
    assert "efa:table" not in book


def test_generated_numbers_match_data():
    """Spot-check: counts in the book are the ledgers', not hand-typed."""
    book = bb.Book(ROOT).generate()
    entries = json.loads((ROOT / "atlas" / "gap_map.json").read_text())["entries"]
    assert f"**{len(entries)} bounded quantities**" in book
    workable = sum(1 for e in entries if bb.is_workable(e))
    assert f"**{workable} witness-workable**" in book
    fence = json.loads((ROOT / "certificates" / "erdos-13" / "table.json").read_text())
    last_exc = max(int(k) for k in fence["exceptions_over_floor_n_over_3_plus_1"])
    assert f"**N = {last_exc} is the last exception in the computed range**" in book
    obs = json.loads((ROOT / "observatory" / "measurements.json").read_text())
    assert f"Completed family points: **{obs['family_points_completed']}**" in book
    # the mandatory emitted-vs-minimal caveat is carried from the data file
    assert "NOT a minimal certificate" in book


def test_prose_stubs_marked_for_lead():
    """Seed edition: every chapter's prose is explicitly a draft."""
    for chap in sorted((ROOT / "book" / "chapters").glob("*.md")):
        assert "<!-- DRAFT: lead pass pending -->" in chap.read_text(encoding="utf-8"), \
            f"{chap.name} missing the draft marker"
