# Foundry progress membrane

This directory is the append-only public edge of the math autoharness. A
CHRONOS research run may publish a **receipt** here only after the deterministic
ingester has parsed all required fields and both the receipt and the Atlas pass
validation.

Receipts are research state, not theorem claims. Their `evidence_class` is
always `provisional` until a human or an exact verifier promotes the underlying
result into `atlas/problems.json` or a certificate directory. The automation is
therefore allowed to push this directory to `automation/frontier-scout`; it is
not allowed to edit canonical Atlas records.

The loop is:

1. the local 35B CHRONOS scout performs one bounded verifier-first action;
2. `tools/foundry.py ingest` converts its labelled cockpit response into a
   typed, content-addressed receipt;
3. repeated blocked/negative receipts open a bounded frontier-consult gate;
4. a frontier model returns strategy advice to the next local research tick;
5. `tools/foundry.py publish` validates and pushes progress only.

Run `python3 tools/foundry.py validate` to verify the receipt ledger.
