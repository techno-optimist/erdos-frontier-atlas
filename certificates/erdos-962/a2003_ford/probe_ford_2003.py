#!/usr/bin/env python3
"""Isolated-mode playback of the unchanged archived probe_original.py.txt.
The original source hash is pinned by verify_ford_2003.py.
"""
import pathlib
import sys as _sys, pathlib as _pathlib  # noqa: E401
_sys.path.insert(0, str(_pathlib.Path(__file__).resolve().parent))
import runpy

HERE = pathlib.Path(__file__).resolve().parent

def main() -> None:
    runpy.run_path(str(HERE / "probe_original.py.txt"), run_name="__main__")

if __name__ == "__main__":
    main()
