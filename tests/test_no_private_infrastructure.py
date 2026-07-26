"""This repository is public and must not describe the machines that produced it.

The rule is that nothing here names private infrastructure: no hostnames, no
private filesystem paths, no internal service names or ports. It is not a
secrecy rule so much as a claim-hygiene one — a reader cannot reproduce anything
that lives on a machine only we can reach, so naming that machine adds nothing
they can use while quietly advertising our topology.

It had drifted. A 2026-07-26 sweep found fifteen references to our private box
across twelve files: one machine-readable field (`"runner": "dgx-11gb"` in a
replay contract) and fourteen prose mentions in quarantine notes of the form
"the private DGX 10^10 run is quarantined until its receipt and runner are
public."

Those quarantine notes are load-bearing honesty and were kept — but note what
the hardware name was contributing to them: nothing. "Private" and "quarantined"
carry the entire meaning for a reader. Dropping the vendor name costs no
epistemic content, which is why the whole sweep was safe to do.

`CHRONOS` is deliberately NOT on the forbidden list: it is the public name of
the agent whose scoreboard this repo carries, not a piece of infrastructure.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SELF = pathlib.Path(__file__).name

# Each entry: (regex, why it must not appear)
FORBIDDEN = [
    (r"\bdgx\b", "names our private compute box"),
    (r"spark-[0-9a-f]{4}", "private hostname"),
    (r"/home/chronos", "private filesystem path"),
    (r"\bsglang\b", "private inference service"),
    (r"\btailscale\b", "private network fabric"),
    (r"chronos-agent", "private agent deployment name"),
    (r"localhost:(?:8198|8199|30000)", "private service port"),
    (r"/Users/[a-z]+/", "absolute path from a developer's machine"),
]

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules"}
# Binary-ish payloads a text scan would only produce noise on.
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".g6", ".pyc"}


def _repo_files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in SKIP_SUFFIXES:
            continue
        # This file necessarily contains the patterns it forbids.
        if p.name == SELF:
            continue
        yield p


def test_no_private_infrastructure_references():
    hits = []
    for path in _repo_files():
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pattern, why in FORBIDDEN:
            for m in re.finditer(pattern, text, re.I):
                line = text.count("\n", 0, m.start()) + 1
                rel = path.relative_to(ROOT)
                hits.append(f"{rel}:{line}: {m.group(0)!r} — {why}")
    assert not hits, (
        "private-infrastructure references in a PUBLIC repository:\n  "
        + "\n  ".join(sorted(hits))
        + "\n\nIf the sentence is a quarantine note, keep the note and drop the "
          "machine name: 'private' and 'quarantined' carry the meaning a reader "
          "needs, the hardware name does not."
    )
