"""The AI-claim overlay must never be able to promote a claim into a status.

Third parties publish claimed AI-assisted resolutions of Erdos problems faster
than anyone can check them. Recording that a claim exists is useful triage; it
tells an agent where not to duplicate effort and where verification would pay.
Letting a claim *set* a status would be the opposite of useful, and this
repository has already paid for that lesson once, on #552, where its own new-value
claim had to be retracted after publication.

So the rule is mechanical, not aspirational: `status_changed_by_this_claim` must
be false on every entry, an independent verdict stronger than "not checked" must
cite a replayable certificate, and the overlay's copy of each status must agree
with the hub it annotates.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_overlay_validates():
    p = subprocess.run([sys.executable, "tools/validate_ai_claims.py"],
                       cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr


def test_no_claim_changed_a_status():
    doc = json.loads((ROOT / "atlas" / "ai_claims.json").read_text(encoding="utf-8"))
    offenders = [e["erdos_id"] for e in doc["entries"]
                 if e.get("status_changed_by_this_claim") is not False]
    assert not offenders, f"claims were allowed to move a status: {offenders}"


def test_every_claim_is_sourced():
    doc = json.loads((ROOT / "atlas" / "ai_claims.json").read_text(encoding="utf-8"))
    unsourced = [e["erdos_id"] for e in doc["entries"] if not e.get("claim_sources")]
    assert not unsourced, f"claims with no source link: {unsourced}"


def test_overlay_only_annotates_problems_the_hub_indexes():
    doc = json.loads((ROOT / "atlas" / "ai_claims.json").read_text(encoding="utf-8"))
    hub = {int(p["id"]) for p in
           json.loads((ROOT / "atlas" / "stubs.json").read_text(encoding="utf-8"))["problems"]}
    stray = [e["erdos_id"] for e in doc["entries"] if e["erdos_id"] not in hub]
    assert not stray, f"overlay annotates problems absent from the hub: {stray}"
