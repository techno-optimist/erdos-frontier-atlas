"""State of the Frontier report (WS1 / EFA-DR1): contract tests."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "state_of_frontier", ROOT / "tools" / "state_of_frontier.py")
sof = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sof)


def _entries():
    return json.loads((ROOT / "atlas" / "gap_map.json").read_text())["entries"]


def test_deterministic():
    """Two generations from the same data are byte-identical (no timestamps)."""
    assert sof.generate() == sof.generate()


def test_committed_view_is_current():
    """views/state_of_frontier.md must match a regeneration from the data."""
    p = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "state_of_frontier.py"), "--check"],
        capture_output=True, text=True)
    assert p.returncode == 0, f"stale view:\n{p.stdout}\n{p.stderr}"


def test_counts_in_report_match_data():
    entries = _entries()
    report = sof.generate()
    workable = [e for e in entries if sof.is_workable(e)]
    assert f"**{len(entries)} bounded quantities**" in report
    assert f"## Witness-workable quantities ({len(workable)})" in report
    # every workable entry appears as a linked row; no non-workable problem row count drift
    rows = [ln for ln in report.splitlines()
            if ln.startswith("| [#") and "erdosproblems.com" in ln]
    assert len(rows) == len(workable)


def test_workable_filter_is_the_documented_one():
    """The mechanical filter stays exactly as stated in the report text."""
    for e in _entries():
        expected = (e["status"] == "open"
                    and e["witness_side"] != "none"
                    and e["witness_feasibility"] in ("open-easy", "plausible"))
        assert sof.is_workable(e) == expected


def test_board_rows_parse():
    rows = sof.parse_board_rows((ROOT / "README.md").read_text(encoding="utf-8"))
    assert len(rows) >= 5                       # the board is populated
    for row in rows:
        assert len(row) == 5                    # tier|problem|movement|certificate|when


def test_confidence_distribution_rendered():
    entries = _entries()
    report = sof.generate()
    for cls in ("C0", "C1", "C2", "C3"):
        n = sum(1 for e in entries if e["confidence"] == cls)
        assert f"| {cls} | {sof.CLASS_MEANING[cls]} | {n} |" in report


def test_markdown_table_cells_escape_pipes():
    """Data strings containing '|' must not break table rows."""
    assert sof.md_escape("p | n => p^2 | n") == "p \\| n => p^2 \\| n"
    assert sof.md_escape("x" * 100, limit=10).endswith("…")
    # collapsed whitespace keeps rows single-line
    assert "\n" not in sof.md_escape("a\nb")
