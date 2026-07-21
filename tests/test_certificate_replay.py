"""Every certificate script must survive its own documented replay invocation.

Certificates are advertised as `python3 -I <script>` -- the `-I` matters, it is what keeps a replay
hermetic against the reader's site-packages. But `-I` implies `-P`, which drops the script's own
directory from sys.path, so any script importing a SIBLING module dies with ModuleNotFoundError.

This bit us twice in one day (jc-family-fences, then ringel-nonstretchability) and each time the
symptom was the same: our own published replay instructions produced a traceback for anyone who
followed them. A stranger who cannot run the command cannot check the claim, which is the whole
product. So it is a test now, not a habit.
"""
import pathlib
import re

CERTS = pathlib.Path(__file__).resolve().parent.parent / "certificates"
SHIM = "_pathlib.Path(__file__).resolve().parent"


def _sibling_importers_without_shim():
    bad = []
    for d in sorted(p for p in CERTS.iterdir() if p.is_dir()):
        mods = {f.stem for f in d.rglob("*.py")}
        for f in sorted(d.rglob("*.py")):
            src = f.read_text(errors="ignore")
            if SHIM in src:
                continue
            for line in src.split("\n"):
                m = re.match(r"^(?:import|from)\s+([a-z_0-9]+)", line)
                if m and m.group(1) in mods and m.group(1) != f.stem:
                    bad.append(f"{f.relative_to(CERTS.parent)} imports sibling '{m.group(1)}'")
                    break
    return bad


def test_sibling_imports_survive_isolated_mode():
    bad = _sibling_importers_without_shim()
    assert not bad, (
        "These scripts import a sibling module but lack the sys.path shim, so the documented\n"
        "`python3 -I <script>` replay will fail with ModuleNotFoundError:\n  "
        + "\n  ".join(bad)
        + "\n\nAdd the shim immediately before the sibling import (see certificates/README.md)."
    )
