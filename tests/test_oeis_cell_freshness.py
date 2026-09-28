"""tools/oeis_cell_freshness.py parses OEIS records and flags covered cells, offline."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "oeis_cell_freshness.py"
spec = importlib.util.spec_from_file_location("oeis_cell_freshness", TOOL)
ocf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ocf)

# A made-up record in the OEIS internal format (not real OEIS text).
FAKE = "\n".join([
    "%I A999999 #1",
    "%S A999999 1,2,3,5,8,",
    "%T A999999 13,21",
    "%N A999999 A made-up record for tests.",
    '%H A999999 Someone, <a href="/A999999/b999999.txt">Table of n, a(n) for n = 0..40</a>',
    '%H A999999 Someone else, <a href="/A999999/a999999.txt">Table of n, a(n) for n = 0..90'
    ' with -1 for unknown entries</a>',
    "%O A999999 0,2",
]) + "\n"


def test_parse_seq():
    info = ocf.parse_seq(FAKE, "A999999")
    assert info["offset"] == 0 and info["data_end"] == 6
    assert info["tables"] == [(0, 40, False), (0, 90, True)]


def test_assess():
    info = ocf.parse_seq(FAKE, "A999999")
    assert ocf.assess(6, info) == "COVERED"      # inside the data
    assert ocf.assess(40, info) == "COVERED"     # inside a clean table
    assert ocf.assess(41, info) == "COVERED?"    # only a table with placeholders reaches it
    assert ocf.assess(91, info) == "open"


def test_cell_index():
    assert ocf.cell_index("A999999(41) — first uncomputed cell", "A999999") == 41
    assert ocf.cell_index("i(9) — largest n such that ...", "A999999") is None
    assert ocf.cell_index("A999999 extension — ...", "A999999") is None


def test_report_end_to_end(tmp_path):
    seq = tmp_path / "seq"
    seq.mkdir()
    (seq / "A999999.seq").write_text(FAKE, encoding="utf-8")
    rows = [("A999999(5) — x", "open"), ("A999999(60) — y", "open"),
            ("A999999(95) — z", "open"), ("A999999(3) — w", "closed")]
    gm = {"entries": [{"problem": i + 1, "oeis": "A999999", "quantity": q, "status": s}
                      for i, (q, s) in enumerate(rows)]}
    (tmp_path / "gap_map.json").write_text(json.dumps(gm), encoding="utf-8")
    out = subprocess.run([sys.executable, "-I", str(TOOL), "--seq-dir", str(seq),
                          "--gap-map", str(tmp_path / "gap_map.json")],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert "COVERED   #1     A999999(5)" in out.stdout
    assert "COVERED?  #2     A999999(60)" in out.stdout
    assert "#3 " not in out.stdout and "#4 " not in out.stdout
    assert "3 open cells checked: 1 covered, 1 covered only by a table with placeholders, 1 open" \
        in out.stdout
