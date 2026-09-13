#!/usr/bin/env python3
"""Recompute the substrate board; never overwrite it."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import query_substrate  # noqa: E402

BOARD = pathlib.Path(__file__).resolve().parent / "BOARD.md"


def main():
    got = query_substrate.render_board()
    saved = BOARD.read_text(encoding="utf-8")
    assert saved == got, "BOARD.md stale; rerun query_substrate.board and replace"
    print("verified: BOARD.md matches query_substrate.render_board()")


if __name__ == "__main__":
    main()
