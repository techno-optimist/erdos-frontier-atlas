#!/usr/bin/env python3
"""Validate (or regenerate) any crater by slug -- the generic sibling of
tools/validate_jc_crater.py.

  python3 tools/validate_crater.py <slug>            # validate + drift-check
  python3 tools/validate_crater.py <slug> --write    # regenerate the view + map

Identical to `python3 tools/crater.py validate <slug>`; this spelling exists so
CI can call one file per crater without learning the sub-command grammar.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import craterlib  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main(argv):
    slugs = [a for a in argv if not a.startswith("-")]
    if len(slugs) != 1:
        raise SystemExit("usage: validate_crater.py <slug> [--write]")
    cfg = ROOT / "atlas" / slugs[0] / "crater.json"
    if not cfg.exists():
        raise SystemExit(f"no crater config at {cfg.relative_to(ROOT)}")
    spec = craterlib.load_config(cfg, root=ROOT)
    return craterlib.validate(spec, write="--write" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
