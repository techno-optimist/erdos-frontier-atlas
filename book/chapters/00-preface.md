> **STATUS: SEED EDITION — this book accretes as the frontier moves; it
> circulates externally only after the EFA-DR1 DOI is live and the first
> observatory note exists.**

# Cartography of Numbers

*The living book of frontier cartography — the observational practice of the
mathematical frontier.*

<!-- DRAFT: lead pass pending -->

Conway drew maps of number-theoretic objects — the topograph; Hatcher built a
book on that map; this book maps the frontier itself. Both are cited here as
inspiration only: nothing below derives from either work.

This is a **living book**. The prose is hand-written; every table, count, and
number is generated at build time from the repository's ledgers
([`atlas/gap_map.json`](../atlas/gap_map.json), the certificates, the
observatory records, the Frontier Board) and carries its confidence class where
one applies. When the data moves, the book moves — and when the book falls
behind the data, the build gate (`make check-book`) fails loudly rather than
letting a stale number circulate. A static text about a moving frontier would
be wrong within weeks; this one is wrong for at most one build.

It is written for two audiences at once: **agents** joining the practice, who
need the field's objects, gates, and honest scope in one place before touching
the ledgers; and **humans** — mathematicians, tool-builders, skeptics — who
want to check, use, or attack the map. The charter
([`FRONTIER_CARTOGRAPHY.md`](../FRONTIER_CARTOGRAPHY.md)) is the field's
normative document; this book is its narrative form. Where they disagree, the
charter wins.

The state of this edition, generated from the data:

```efa:table edition_state
```
