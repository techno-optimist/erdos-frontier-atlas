#!/usr/bin/env python3
"""jc_root_tripwire -- literature-freshness watch for the JC crater's root claim.

Every one of the 30 computed statuses in atlas/jc-crater/computed_statuses.json
is conditional on ONE external fact: Levent Alpöge's 2026-07-19 announcement of
an explicit dim-3 counterexample to the Jacobian Conjecture, currently
"awaiting confirmation" (widely machine-verified, not yet peer-reviewed). There
is no arXiv id for that announcement at the time this tripwire was written --
see atlas/jc-crater/root_claim.json for the full identity record. Nothing in
this repo watches for that claim status changing; tools/validate_jc_crater.py
staleness-gates the GENERATED VIEW (statuses vs. the committed graph), not the
CLAIM the graph is rooted in. This script is that missing instrument.

WHAT THIS DOES NOT DO -- read this before trusting a clean run:
  - It is a KEYWORD tripwire over arXiv abstracts/titles, nothing more. It
    cannot read a paper, cannot judge mathematical correctness, and cannot
    distinguish a real retraction from an unrelated paper that happens to use
    the word "gap" or "error" in a different sense.
  - It has FALSE POSITIVES by construction (broad JC-topic queries surface
    ordinary survey/partial-result papers) and, more importantly, it can have
    FALSE NEGATIVES: it CANNOT PROVE THE ABSENCE of a retraction. A retraction
    announced only on social media, in a journal editorial, on Wikipedia's talk
    page, or via a venue arXiv does not itself cover would all be invisible to
    it. Silence from this script is not evidence of continued validity -- it is
    absence of a specific kind of signal from one API.
  - It is a PROMPT FOR HUMAN REVIEW, not a verdict. A "genuine alert" (nonzero
    exit, alert file written) means: a human should read the listed items and
    decide whether atlas/jc-crater/root_claim.json's status field needs
    updating, and whether atlas/jc-crater/README.md's "Root-claim freshness"
    note needs to change. It does not mean the crater is wrong.
  - It watches the CLAIM (authorship / priority / peer-review status), never
    the OBJECT. certificates/jacobian-conjecture/verify.py independently
    re-verifies the exhibited map's arithmetic every time it is run, and nothing
    here bears on that. See root_claim.json's "claim_vs_object_distinction".

WHAT IT DOES:
  1. If atlas/jc-crater/root_claim.json names an arxiv_id, fetches that record
     directly (id_list query) so a later-assigned id can be added by hand and
     picked up immediately.
  2. Polls export.arxiv.org's public API (no auth) with a handful of
     Jacobian-Conjecture-shaped queries: title/abstract match, and an author
     query for Alpöge (in case the formal write-up lands on arXiv).
  3. Classifies every fetched item's title+abstract against keyword classes
     associated with retraction/erratum/refutation/confirmation signals
     (see CLASS_PATTERNS). This is regex string matching -- nothing semantic.
  4. Diffs against state/last-seen ids (root_claim_state.json) so re-running
     is idempotent: an item already seen never re-triggers an alert, even if
     it still matches a signal class.
  5. Writes root_claim_alert.json (deleted on the next successful run that
     no longer wants an unreviewed alert -- more precisely, it is REWRITTEN
     to hold exactly the current set of unreviewed hits) only when there is
     at least one NEW classified hit; exits nonzero exactly then.
  6. On any network failure, exits 0 (so crontab treats it as non-fatal) but
     writes freshness: "UNKNOWN" into the state file rather than a false
     all-clear -- silence from arXiv is not the same as a clean bill of health.

Usage:
  python3 tools/jc_root_tripwire.py            # poll, update state, maybe alert
  python3 tools/jc_root_tripwire.py --dry-run  # poll and print, write nothing

Exit codes:
  0   ran to completion with no NEW classified hit (includes: network
      unreachable -> freshness UNKNOWN; this is NOT an all-clear, see above)
  1   at least one NEW item matched a signal class -- read
      atlas/jc-crater/root_claim_alert.json and review by hand
  2   local state/config error (malformed root_claim.json, etc.)
"""
from __future__ import annotations

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
CRATER = ROOT / "atlas" / "jc-crater"
ROOT_CLAIM = CRATER / "root_claim.json"
STATE = CRATER / "root_claim_state.json"
ALERT = CRATER / "root_claim_alert.json"

NS = {"a": "http://www.w3.org/2005/Atom"}
API = "http://export.arxiv.org/api/query?{qs}"
USER_AGENT = "jc-crater-tripwire/1 (erdos-frontier-atlas; contact via repo)"
TIMEOUT_S = 45
POLITENESS_DELAY_S = 3  # arXiv API etiquette between successive queries

# Broad topical net (expected to include ordinary, unrelated JC-literature
# papers -- that is a known and accepted false-positive source, not a bug).
TOPIC_QUERIES = [
    'ti:"Jacobian conjecture"',
    'abs:"Jacobian conjecture"',
    'au:Alpoge AND abs:Jacobian',
]

# Keyword classes for candidate retraction/erratum/refutation/confirmation
# signals. Deliberately coarse regexes over title+abstract text -- see the
# module docstring for why this cannot be a verdict. Each class is checked
# independently so an alert names WHICH kind of language triggered it.
CLASS_PATTERNS = {
    "withdrawn": re.compile(r"\bwithdrawn\b", re.I),
    "retracted": re.compile(r"\bretract(ed|ion)?\b", re.I),
    "erratum": re.compile(r"\berratum\b|\bcorrigendum\b", re.I),
    "gap_or_flaw": re.compile(r"\b(gap|flaw|error|mistake)\b\s+\b(in|found|discovered)\b"
                               r"|\b(in|found|discovered)\b\s+\b(a|the)?\s*(gap|flaw|error|mistake)\b",
                               re.I),
    "counter_to_counterexample": re.compile(
        r"\bcounterexample to (the )?counterexample\b"
        r"|\brefut(e|es|ed|ing|ation)\b.{0,40}\balp[oö]ge\b"
        r"|\balp[oö]ge\b.{0,40}\b(incorrect|wrong|flawed|invalid)\b", re.I),
    "confirmation_or_publication": re.compile(
        r"\bconfirm(ed|ation|s)?\b|\bpeer[- ]review(ed)?\b"
        r"|\baccepted (for|to|in) publication\b|\bpublished in\b|\bto appear in\b", re.I),
}


def fail(msg: str) -> "SystemExit":
    return SystemExit(f"jc_root_tripwire ERROR: {msg}")


def load_root_claim() -> dict:
    if not ROOT_CLAIM.exists():
        raise fail(f"{ROOT_CLAIM} missing -- the tripwire has nothing to watch "
                    "without the claim identity record")
    try:
        rc = json.loads(ROOT_CLAIM.read_text())
    except ValueError as exc:
        raise fail(f"{ROOT_CLAIM} is not valid JSON: {exc}")
    if rc.get("schema") != "efa-jc-root-claim/v1":
        raise fail(f"{ROOT_CLAIM}: bad or missing schema tag")
    for field in ("claim", "object_certificate"):
        if field not in rc:
            raise fail(f"{ROOT_CLAIM}: missing '{field}'")
    return rc


def load_state() -> dict:
    if not STATE.exists():
        return {"seen": {}, "last_run": None, "last_freshness": None, "runs": 0}
    try:
        return json.loads(STATE.read_text())
    except ValueError:
        # Corrupt state file: start clean rather than crash a cron job: the
        # cost is at most one re-surfaced alert for already-seen items, which
        # a human reviews once -- safer than silently never running again.
        return {"seen": {}, "last_run": None, "last_freshness": None, "runs": 0}


# Some Python installs (notably the python.org macOS installer, which ships
# without running "Install Certificates.command") have no configured default
# CA bundle and fail every HTTPS request with CERTIFICATE_VERIFY_FAILED even
# when the network is fine. If that happens, fall back to the OS's own CA
# bundle if one of the usual paths exists -- verification stays ON throughout
# (never CERT_NONE); this only supplies a cert store, it does not weaken TLS.
_SYSTEM_CA_CANDIDATES = (
    "/etc/ssl/cert.pem",                       # macOS
    "/etc/ssl/certs/ca-certificates.crt",       # Debian/Ubuntu
    "/etc/pki/tls/certs/ca-bundle.crt",         # RHEL/Fedora
)


def _fallback_ssl_context():
    for path in _SYSTEM_CA_CANDIDATES:
        if os.path.exists(path):
            try:
                return ssl.create_default_context(cafile=path)
            except ssl.SSLError:
                continue
    return None


def arxiv_get(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            return ET.fromstring(resp.read())
    except urllib.error.URLError as exc:
        is_cert_error = isinstance(getattr(exc, "reason", None), ssl.SSLCertVerificationError) \
            or "CERTIFICATE_VERIFY_FAILED" in str(exc)
        if not is_cert_error:
            raise
        ctx = _fallback_ssl_context()
        if ctx is None:
            raise
        with urllib.request.urlopen(req, timeout=TIMEOUT_S, context=ctx) as resp:
            return ET.fromstring(resp.read())


def parse_entries(root: ET.Element):
    for e in root.findall("a:entry", NS):
        raw_id = (e.findtext("a:id", "", NS) or "").strip()
        yield {
            "id": raw_id.rsplit("/", 1)[-1] if raw_id else "",
            "title": " ".join((e.findtext("a:title", "", NS) or "").split()),
            "summary": " ".join((e.findtext("a:summary", "", NS) or "").split()),
            "published": e.findtext("a:published", "", NS),
            "updated": e.findtext("a:updated", "", NS),
            "url": raw_id,
        }


def classify(item: dict):
    """Return the sorted list of signal-class names this item's title+summary
    match. Empty list = ordinary topical hit, not a candidate signal."""
    text = f"{item['title']} {item['summary']}"
    return sorted(name for name, pat in CLASS_PATTERNS.items() if pat.search(text))


def bears_on_root(item: dict, announced: str) -> bool:
    """True iff this item could possibly speak to the root claim's STATUS.

    Relevance gate, deliberately crude and deliberately one-directional: a
    paper whose latest version predates the announcement cannot be a
    retraction, erratum, refutation or confirmation OF that announcement, no
    matter what words its abstract contains. Without this gate the topical
    queries surface decades of ordinary Jacobian-Conjecture literature and any
    abstract containing e.g. "confirm" raises a false alert (observed: a 2022
    plane-JC degree-bound paper). Dropping pre-announcement items costs us
    nothing the tripwire was ever able to detect, and items are still recorded
    as seen, so the log stays complete."""
    stamp = item.get("updated") or item.get("published") or ""
    return stamp[:10] >= announced[:10] if stamp else True


def fetch_all(root_claim: dict, log):
    """Yield (item, source_query) for the direct id lookup (if any) and every
    topic query, sleeping between requests per arXiv API etiquette. Raises on
    the first network-level failure -- the caller treats that as UNKNOWN, not
    all-clear."""
    arxiv_id = (root_claim.get("claim") or {}).get("arxiv_id")
    queries = []
    if arxiv_id:
        queries.append(("id_list", f"id_list={urllib.parse.quote(arxiv_id)}"))
    for q in TOPIC_QUERIES:
        qs = (f"search_query={urllib.parse.quote(q)}"
              "&sortBy=submittedDate&sortOrder=descending&max_results=25")
        queries.append((q, qs))

    for label, qs in queries:
        url = API.format(qs=qs)
        root = arxiv_get(url)  # network exceptions propagate to caller
        n = 0
        for item in parse_entries(root):
            if item["id"]:
                n += 1
                yield item, label
        log.append(f"query {label!r}: {n} entries")
        time.sleep(POLITENESS_DELAY_S)


def main(argv) -> int:
    dry_run = "--dry-run" in argv
    root_claim = load_root_claim()
    state = load_state()
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    announced = (root_claim.get("claim") or {}).get("announced") or "0000-00-00"
    log = []

    try:
        fetched = list(fetch_all(root_claim, log))
        freshness = "OK"
        network_error = None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            ConnectionError, ET.ParseError, OSError) as exc:
        fetched = []
        freshness = "UNKNOWN"
        network_error = f"{type(exc).__name__}: {exc}"

    new_hits = []       # any never-before-seen item, classified or not (for the log)
    new_signal_hits = []  # never-before-seen items that also match a signal class
    for item, source_query in fetched:
        if item["id"] in state["seen"]:
            continue
        state["seen"][item["id"]] = ts
        classes = classify(item)
        relevant = bears_on_root(item, announced)
        record = {**item, "source_query": source_query, "signal_classes": classes,
                  "post_announcement": relevant}
        new_hits.append(record)
        if classes and relevant:
            new_signal_hits.append(record)

    # Bound state growth (mirrors the DGX riemann-lane tripwire's convention).
    if len(state["seen"]) > 3000:
        state["seen"] = dict(sorted(state["seen"].items(), key=lambda kv: kv[1])[-1500:])

    state["last_run"] = ts
    state["last_freshness"] = freshness
    state["runs"] = state.get("runs", 0) + 1
    if network_error:
        state["last_network_error"] = network_error
    else:
        state.pop("last_network_error", None)
    state["last_new_count"] = len(new_hits)
    state["last_signal_count"] = len(new_signal_hits)

    summary = {
        "ts": ts,
        "freshness": freshness,
        "watched_claim_status": (root_claim.get("claim") or {}).get("status"),
        "new_items": len(new_hits),
        "new_signal_hits": len(new_signal_hits),
        "queries_run": log,
    }
    if network_error:
        summary["network_error"] = network_error
        summary["note"] = ("tripwire could not reach arXiv -- freshness UNKNOWN, "
                            "not confirmed-clean. Re-run when network is available.")

    if dry_run:
        print(json.dumps(summary, indent=2))
        if new_signal_hits:
            print(json.dumps(new_signal_hits, indent=2))
        return 1 if new_signal_hits else 0

    CRATER.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2) + "\n")

    if new_signal_hits:
        ALERT.write_text(json.dumps({
            "ts": ts,
            "instructions": (
                "Candidate signal(s) about the JC crater's root claim (see "
                "atlas/jc-crater/root_claim.json). This is a KEYWORD MATCH, not "
                "a verdict -- read each item and judge for yourself whether "
                "root_claim.json's status or atlas/jc-crater/README.md's "
                "'Root-claim freshness' note needs updating. Delete this file "
                "(or let the next clean run overwrite it) once reviewed."),
            "hits": new_signal_hits,
        }, indent=2) + "\n")
        print(json.dumps(summary, indent=2))
        print(json.dumps(new_signal_hits, indent=2))
        return 1

    # No new signal hits: if a stale alert file exists from a prior run,
    # leave it -- clearing it silently would erase an unreviewed alert. A
    # human (or a wrapper script) removes it after review. We only ever
    # WRITE root_claim_alert.json when there is something new to say.
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
