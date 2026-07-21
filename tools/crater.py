#!/usr/bin/env python3
"""crater -- scaffold, list, validate and selftest CRATERS. Stdlib only.

A crater is a directed graph of statements with certified roots, in which every
node's status is COMPUTED from the roots by mechanical propagation along typed,
cited edges. The engine is in tools/craterlib/; each crater declares its own
vocabulary, prose and paths in atlas/<slug>/crater.json.

Usage:
  python3 tools/crater.py list
  python3 tools/crater.py new <slug> [--polarity refuted|proved]
  python3 tools/crater.py validate <slug> [--write]
  python3 tools/crater.py selftest

`validate jc-crater` is exactly what tools/validate_jc_crater.py runs; that
wrapper survives because its CLI is referenced by RESULTS_REGISTRY.md, the
crater README and the skills.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import craterlib  # noqa: E402
from craterlib import scaffold, selftest  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ATLAS = ROOT / "atlas"


def _config_path(slug):
    p = ATLAS / slug / "crater.json"
    if not p.exists():
        raise SystemExit(f"crater: no crater config at {p.relative_to(ROOT)} "
                         f"(try `python3 tools/crater.py list`)")
    return p


def _short_reason(exc):
    """One line, no traceback: whitespace-collapsed and capped, so a broken
    crater costs one row rather than a screen."""
    msg = " ".join(str(exc).split()) or exc.__class__.__name__
    return msg if len(msg) <= 140 else msg[:137] + "..."


def cmd_list(argv):
    """List every crater, degrading PER ROW.

    Several agents share this branch, so a half-scaffolded or half-written
    crater directory is a NORMAL condition, not an anomaly: a crater.json
    written before its implication_graph.json is a race, not corruption. One
    such directory must not cost you the listing of every other crater, and
    must never surface as a raw traceback. Exit non-zero only if EVERY crater
    failed -- one broken crater is a row, an entirely unreadable atlas is a
    failure.
    """
    found = sorted(p for p in ATLAS.glob("*/crater.json"))
    if not found:
        print("no craters found under atlas/")
        return 0
    failures = 0
    for p in found:
        # Directory name is the fallback identity: load_config is itself one of
        # the things that can fail, so spec.slug may never exist.
        slug = p.parent.name
        try:
            spec = craterlib.load_config(p, root=ROOT)
            slug = spec.slug
            g, nodes = craterlib.load_graph(spec)
        except (Exception, SystemExit) as exc:
            # SystemExit is the validators' failure channel (spec.failer) and is
            # NOT an Exception subclass, so it has to be named explicitly.
            failures += 1
            print(f"{slug:<16} {'ERROR':<8} unreadable: {_short_reason(exc)}")
            continue
        print(f"{slug:<16} {spec.polarity:<8} "
              f"{len(nodes)} nodes, {len(g['edges'])} edges")
    if failures:
        print(f"\n{failures} of {len(found)} crater(s) could not be read.")
    return 1 if failures == len(found) else 0


def cmd_new(argv):
    if not argv:
        raise SystemExit("crater new: need a <slug>")
    slug = argv[0]
    polarity = "refuted"
    if "--polarity" in argv:
        polarity = argv[argv.index("--polarity") + 1]
    if polarity not in craterlib.POLARITIES:
        raise SystemExit(f"crater new: polarity must be one of "
                         f"{sorted(craterlib.POLARITIES)}")
    written = scaffold.new_crater(ROOT, slug, polarity, force="--force" in argv)
    for p in written:
        print(f"  created {p.relative_to(ROOT)}")
    print(f"\nnext: fill in atlas/{slug}/implication_graph.json + replace the "
          f"placeholder check,\nthen `python3 tools/crater.py validate {slug} --write`.")
    print("House rule: ship a planted-failure control with it (see "
          "tools/craterlib/selftest.py).")
    return 0


def cmd_validate(argv):
    if not argv:
        raise SystemExit("crater validate: need a <slug>")
    spec = craterlib.load_config(_config_path(argv[0]), root=ROOT)
    return craterlib.validate(spec, write="--write" in argv)


def cmd_selftest(argv):
    _, failed, _ = selftest.run(verbose="--quiet" not in argv)
    return 1 if failed else 0


COMMANDS = {"list": cmd_list, "new": cmd_new, "validate": cmd_validate,
            "selftest": cmd_selftest}


def main(argv):
    if not argv or argv[0] not in COMMANDS:
        print(__doc__.strip())
        return 0 if not argv else 2
    return COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
