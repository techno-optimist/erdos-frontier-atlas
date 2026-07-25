"""Every relative link in a reader-facing page must resolve.

This is not pedantry. `book/BOOK.md` imports the Frontier Board table verbatim from
`README.md`, which lives at the repo ROOT — so a root-relative link like
`](certificates/erdos-13)` silently becomes `book/certificates/erdos-13` and 404s
for anyone reading the book on GitHub. Seven links were broken that way before
build_book.py learned to re-anchor them on import. A broken link in the page we
call the reader's front door is the cheapest possible way to look unserious, and
nothing else in the suite was watching for it.
"""
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = [
    "README.md",
    "FRONTIER_CARTOGRAPHY.md",
    "book/BOOK.md",
    "atlas/walls.md",
    "certificates/README.md",
    "RELEASING.md",
]
LINK = re.compile(r"\]\((?!https?://|#|mailto:)([^)#\s]+)")


def _dead_links(rel):
    p = ROOT / rel
    if not p.exists():
        return []
    base = p.parent
    out = []
    for m in LINK.finditer(p.read_text(encoding="utf-8")):
        target = m.group(1).strip()
        if not target or target.startswith("<"):
            continue
        if not (base / target).exists():
            out.append(f"{rel} -> {target}")
    return out


def test_no_dead_relative_links_in_reader_facing_pages():
    bad = [b for rel in PAGES for b in _dead_links(rel)]
    assert not bad, (
        "relative links that do not resolve (a reader on GitHub gets a 404):\n  "
        + "\n  ".join(bad)
    )


def test_book_board_links_are_reanchored():
    """The board is imported from README (repo root) into book/ — links must be ../."""
    book = ROOT / "book" / "BOOK.md"
    if not book.exists():
        return
    text = book.read_text(encoding="utf-8")
    # a bare root-relative link to a top-level dir is the bug this guards
    offenders = re.findall(r"\]\((certificates|atlas|tools|views|observatory)/", text)
    assert not offenders, (
        "book/BOOK.md contains root-relative links that break one directory down; "
        "build_book.parse_board_rows must re-anchor them with ../ — found: "
        + ", ".join(sorted(set(offenders)))
    )
