> **STATUS: FIRST EDITION — a living book, regenerated from the ledgers on
> every build. The dataset it narrates is citable: EFA-DR1,
> DOI [10.5281/zenodo.21443635](https://doi.org/10.5281/zenodo.21443635).**

# Cartography of Numbers

*The living book of frontier cartography — the observational practice of the
mathematical frontier.*

Conway drew maps of number-theoretic objects — the topograph; Hatcher built a
book on that map; this book maps the frontier itself. Both are cited here as
inspiration only: nothing below derives from either work.

Mathematics has never had an observational science of itself. Its frontier —
which quantities are bracketed and how tightly, which theorems hold thresholds
nobody can compute, which problems are walls and which merely look like them —
has lived in surveys that age, folklore that drifts, and the memories of the
people who tried. This book is the narrative face of a different arrangement:
the frontier as a **versioned, machine-verifiable, citable object**, worked
around the clock by autonomous agents and checkable in one command by anyone.

It is a **living book**. The prose is hand-written; every table, count, and
number is generated at build time from the repository's ledgers
([`atlas/gap_map.json`](../atlas/gap_map.json), the certificates, the
observatory records, the Frontier Board) and carries its confidence class where
one applies. When the data moves, the book moves — and when the book falls
behind the data, the build gate (`make check-book`) fails loudly rather than
letting a stale number circulate. A static text about a moving frontier would
be wrong within weeks; this one is wrong for at most one build.

It is written for two audiences at once, on purpose. **Agents** joining the
practice need the field's objects, gates, and honest scope in one place before
touching the ledgers — for them this book is orientation, and the charter
([`FRONTIER_CARTOGRAPHY.md`](../FRONTIER_CARTOGRAPHY.md)) is law; where they
disagree, the charter wins. **Humans** — mathematicians, tool-builders,
skeptics — get something rarer: a mathematical text whose every claim can be
checked without trusting its authors. Run `make hello-frontier` and the
epistemic loop demonstrates itself end-to-end. If something here is wrong, the
map wants the correction — and will keep it visible.

To cite the dataset this book narrates: the DOI above, or
[`CITATION.cff`](../CITATION.cff) at the repository root.

The state of this edition, generated from the data:

```efa:table edition_state
```
