# Is our table actually Ringel's chirotope? — independent fidelity check

The Lean proof is sound about the table it is given. This directory answers the *separate* question:
**is that table Ringel's object?** Verdict: **CONFIRMED, by primary source, on two independent legs.**

## Why an entry-by-entry diff is impossible

Carroll (arXiv:0704.3424 §8.1) states outright that Ringel's non-Pappus arrangement *"is not even
defined, except by a picture… we could give a chirotope … however, we choose not to."* **No published
sign table exists to diff against.** That is why this link was unpinned — it is not a repo failing.

## Leg A — transcription fidelity

Both affine projections were re-typed from a fresh 2026-07-21 fetch of `oriented.sourceforge.net`
and the table rebuilt independently of this repo: **verbatim identical**, and it reproduces the
payload SHA-256 `9a1a5d57…3d7025b4`. The two projections overlap in **35** triples and agree on all
35 — a 2⁻³⁵ coincidence were either mistranscribed.

## Leg B — uniqueness, not comparison

> "Up to isomorphism this is the only simple nonstretchable arrangement of 9 pseudolines"
> — Richter-Gebert & Ziegler, *Oriented Matroids*, Handbook of DCG 3rd ed., §6.1

Independently corroborated by Celaya–Loho–Yuen (Selecta Math., §4.2) for `Rin(3,9)`. So it suffices to
show our table is a **uniform rank-3 chirotope** and **non-realizable** — both established here from
scratch. Identity for an oriented matroid means up to relabelling and reorientation, which is exactly
what uniqueness delivers. This leg uses no database.

| check | script | outcome |
|---|---|---|
| exchange axiom (B2″), all 531,441 pairs | `chirotope_axioms.py` | PASS, 0 violations |
| 630 three-term Grassmann–Plücker relations | `chirotope_axioms.py` | PASS |
| uniform (84 entries ±1; 64 +, 20 −) ⇒ simple | `chirotope_axioms.py` | PASS |
| **independent** non-realizability — fresh biquadratic final polynomial via Gordan/Farkas, exact `Fraction` simplex, 1260 strict inequalities | `bfp_nonrealizability.py` | NON-REALIZABLE, support 17 |
| positive control: same pipeline on a realizable order type | `bfp_nonrealizability.py` | correctly finds **no** certificate |
| structural fingerprint: 10 mutations; flip each | `mutation_fingerprint.py` | exactly **one** (χ(3,5,7)) stays non-realizable, other **nine** become realizable — each with an explicit integer realization |

That last row reproduces Richter-Gebert & Ziegler §6.3.3 *verbatim*: *"if any one of the triangles …
other than the central one is flipped, we obtain a realizable pseudoline arrangement."* An independent
structural signature of the published object, matched exactly.

## What this check found that was worse than documented

Of the 84 entries: **35** are cross-checked by both projections, **42** are single-read, and **7 were
never transcribed at all** — the χ(0,i,7) family, *inferred* from the line-at-infinity argument. **Two
of those seven are load-bearing in the Lean proof.**

Closed by exhaustion (`inferred_entries_joint_test.py`): of all 2⁷ = 128 assignments to those cells,
only **5** yield a valid chirotope, and of those **only ours is non-realizable** — the other four have
explicit integer realizations. The inference is therefore uniquely pinned by chirotope-hood plus
non-realizability, not by the eye.

## Single-source dependency, now removed

Both the table and eq. (96) traced to one person: `oriented.sourceforge.net` is Carroll's project and
arXiv:0704.3424 is Carroll's preprint, **never journal-published**. The independent final polynomial
here removes the eq.-(96) dependency; the uniqueness argument removes the database dependency.

## No conflict with the Lean file

The Lean note says no certificate exists using 3-term relations alone; the check here uses only
3-term relations. Different objects: Lean's is a linear combination of **syzygies in the bracket
ring**; this is a Farkas combination of **inequalities in log|bracket| space**.

## Citations (corrected)

* Ringel, *Teilungen der Ebene durch Geraden oder topologische Geraden*, Math. Z. **64** (1956) 79–102,
  [10.1007/BF01166556](https://doi.org/10.1007/BF01166556). **Ringel 1956 does not publish the chirotope.**
* The affine projections are renderings in **Carroll's** example database, not Ringel's own figures.
* Eq. (96): Carroll arXiv:0704.3424, who states he takes it from BLVSWZ 2nd ed., p. 349.
