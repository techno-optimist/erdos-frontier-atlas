"""Upstream's finite-handle states must not be flattened into plain "open".

erdosproblems.com distinguishes several kinds of open. Three of them name a
FINITE handle on the problem, which is this atlas's entire subject:

    decidable    resolved up to a finite check
    falsifiable  a finite counterexample would settle it
    verifiable   a finite check would settle it

Our stub compiler treats all three as "open" for the status field, which is
correct — they are open. But an earlier version recorded *only* that, so 43
problems that a finite computation could move looked exactly like the 608 that
it cannot. Seven of the 43 carry a prize, including a $1000 falsifiable (#64)
and a $500 decidable (#19), and this repository's front page had claimed no
Erdos prize here was finitely claimable.

Losing that signal is the most expensive kind of data loss for a computational
frontier atlas: it hides the targets among the walls.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
HANDLES = {"decidable", "falsifiable", "verifiable"}


def _problems():
    return json.loads((ROOT / "atlas" / "stubs.json").read_text(encoding="utf-8"))["problems"]


def test_finite_handle_is_recorded_wherever_upstream_names_one():
    missing = [p["id"] for p in _problems()
               if p.get("upstream_state_raw") in HANDLES
               and p.get("upstream_finite_handle") != p.get("upstream_state_raw")]
    assert not missing, (
        f"upstream names a finite handle for these problems but the stub does not "
        f"record it: {missing}. Flattening decidable/falsifiable/verifiable into "
        f"plain 'open' hides the targets among the walls.")


def test_handle_is_never_invented():
    bogus = [p["id"] for p in _problems()
             if p.get("upstream_finite_handle")
             and p["upstream_finite_handle"] != p.get("upstream_state_raw")]
    assert not bogus, f"finite handle disagrees with the upstream state on: {bogus}"


def test_the_handled_set_is_not_silently_empty():
    """A regression that dropped the field entirely would pass the checks above."""
    handled = [p for p in _problems() if p.get("upstream_finite_handle")]
    assert len(handled) >= 20, (
        f"only {len(handled)} problems carry a finite handle; upstream had 43 at "
        f"the 2026-07-26 pin, so a large drop means the field stopped being read")
