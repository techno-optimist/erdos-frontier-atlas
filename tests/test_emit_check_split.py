"""A verifier must not rewrite its own receipt on an ordinary replay.

Emitting and checking on the same code path is how a committed receipt that
disagrees with its verifier gets silently overwritten instead of reported — the
defect that let N11_L7_S7 carry `vertex_count: 117` while its own verifier
produced 136. The fix is a split: replay COMPARES, and only an explicit `--emit`
rewrites.

These tests pin the split for the lane that has been converted, and pin the
coverage convention that makes converting SAFE to do: a check-only verifier
re-derives its receipt without touching the file, so mtime cannot see it. It
declares the fact with a `receipt-checked: <file>` line, and the drift gate
counts that as coverage. Without that convention, converting a verifier to
check-only — exactly the behaviour we want — would make the coverage number look
worse, and the metric would punish the fix.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANE = ROOT / "certificates" / "fibonacci-macro-residual"
CONVERTED = sorted(LANE.glob("verify_n*_routability.py"))


def test_lane_has_converted_verifiers():
    assert CONVERTED, "expected the routability verifiers to exist"


def test_replay_does_not_rewrite_the_receipt():
    """The core property: an ordinary replay leaves the receipt byte-identical."""
    for v in CONVERTED:
        receipts = list(LANE.glob("N*_COMPLETE.json"))
        before = {p: p.read_bytes() for p in receipts}
        p = subprocess.run([sys.executable, "-I", v.name], cwd=LANE,
                           capture_output=True, text=True, timeout=300)
        assert p.returncode == 0, f"{v.name} failed on clean replay:\n{p.stdout}\n{p.stderr}"
        for path, blob in before.items():
            assert path.read_bytes() == blob, (
                f"{v.name} rewrote {path.name} on a plain replay; emitting belongs "
                f"behind --emit")


def test_replay_detects_a_poisoned_receipt():
    """It must FAIL on drift, not absorb it. A checker that cannot fail is not one."""
    v = LANE / "verify_n6_l3_s3_routability.py"
    target = LANE / "N6_L3_S3_COMPLETE.json"
    if not (v.exists() and target.exists()):
        return
    original = target.read_bytes()
    try:
        d = json.loads(original)
        d["n_columns"] = 999999
        target.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")
        p = subprocess.run([sys.executable, "-I", v.name], cwd=LANE,
                           capture_output=True, text=True, timeout=300)
        assert p.returncode != 0, "poisoned receipt was NOT detected"
        assert "RECEIPT DRIFT" in (p.stdout + p.stderr)
    finally:
        target.write_bytes(original)


def test_check_only_declares_coverage():
    """`receipt-checked:` is what lets the drift gate see check-only verification."""
    for v in CONVERTED:
        src = v.read_text()
        assert "receipt-checked:" in src, (
            f"{v.name} verifies check-only but does not declare which receipt it "
            f"checked, so tools/check_receipt_drift.py will score it as never "
            f"re-derived")
