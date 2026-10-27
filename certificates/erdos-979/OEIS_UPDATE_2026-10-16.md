# Note: stronger published bound on A385316(6) (added 2026-10-26)

This note extends the frozen certificate; `RECEIPT.md` and `verify.py` are unchanged.

`RECEIPT.md` and `verify.py` were written when the A385316 comments published only
`a(6) > 499243435237 (≈4.99·10¹¹)`. That is out of date. As of revision 38,
[OEIS A385316](https://oeis.org/A385316) carries the comment:

> a(6) > 3.166*10^14, if it exists. - Morfis Sallis, Oct 16 2026

So the certificate here does **not** improve the published bound and is not the
best known bound. What it still is: a replayable, exhaustive check that no
`N ≤ 10¹²` has exactly six prime-cube representations (`a(6) > 10¹²`), with
`a(1..5)` reproduced exactly as a fail-closed self-check. We have not
independently checked the `3.166·10¹⁴` bound; it is quoted from OEIS.
