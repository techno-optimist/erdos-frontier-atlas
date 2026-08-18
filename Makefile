# Erdős Frontier Atlas — release-kit targets (EFA-DR1)
#
#   make hello-frontier      the 10-minute quickstart: replay a DRAT certificate
#                            (+ negative control), re-verify a witness certificate,
#                            read one gap-map entry with its confidence class.
#                            Needs only git + cc + python3.
#   make state-of-frontier   regenerate views/state_of_frontier.md from the data
#   make check-views         fail if views/state_of_frontier.md is stale
#   make book                rebuild book/BOOK.md ("Cartography of Numbers") from
#                            book/chapters/*.md + the live ledgers
#   make check-book          fail if book/BOOK.md is stale vs the data
#   make graph               rebuild the attack graph (atlas/graph/ +
#                            views/sorties.md + views/graph/ cards) — see GRAPH.md
#   make check-graph         fail if any graph output is stale or breaks a rule
#   make validate            gap-map validator (dependency-free) + full atlas
#                            integrity check (needs: pip install -r requirements-dev.lock)
#   make verify-certs        replay every fast in-repo certificate verifier
#   make test                pytest over tests/

.PHONY: hello-frontier state-of-frontier check-views book check-book graph check-graph validate verify-certs test check-contracts replay-contracts-fast replay-contracts-slow audit-fast audit-slow

hello-frontier:
	bash scripts/hello_frontier.sh

state-of-frontier:
	python3 tools/state_of_frontier.py

check-views:
	python3 tools/state_of_frontier.py --check

book:
	python3 book/build_book.py

check-book:
	python3 book/build_book.py --check

graph:
	python3 tools/build_graph.py

check-graph:
	python3 tools/build_graph.py --check
	python3 tools/validate_graph.py

validate:
	python3 tools/validate_gap_map.py
	python3 tools/validate_ai_claims.py
	python3 tools/validate_atlas.py

# The sub-10-second certificate replays. certificates/erdos-979 is excluded here
# only because its headline run needs numpy + ~11 GB RAM (~80 s) — see
# certificates/erdos-979/RECEIPT.md for its replay command. The ramsey-3-3 DRAT
# replay (incl. negative control) runs inside `make hello-frontier`.
verify-certs:
	python3 certificates/erdos-552/verify.py
	python3 certificates/erdos-552-f39/verify.py
	python3 certificates/erdos-13/verify.py
	python3 certificates/erdos-1107/verify.py 200000
	python3 -I certificates/erdos-142-cone-obstruction/verify.py
	python3 -I certificates/erdos-142-mirror-core-additive-wall/verify.py
	python3 -I certificates/erdos-142-d4-role-distinct-additive-wall/verify.py --self-test
	python3 -I certificates/erdos-142-q24-cylinder-hypograph-wall/verify.py --self-test
	python3 -I certificates/erdos-142-q24-second-orbit-cylinder-hypograph-wall/verify.py --self-test
	python3 -I certificates/erdos-142-q6-pair-coordinate-walls/verify.py --self-test
	python3 -I certificates/erdos-142-q6-global-potential-walls/verify.py --self-test
	python3 -I certificates/erdos-142-q6-all-maximizer-three-row-torsion-wall/verify.py --self-test
	python3 -I certificates/erdos-142-q6-outer-code-tensor-wall/verify.py --self-test
	python3 -I certificates/erdos-142-q6-coordinate-d4-product-wall/verify.py --self-test
	python3 -I certificates/erdos-142-q6-117-cell-six-deletion-wall/verify.py certificates/erdos-142-q6-117-cell-six-deletion-wall/rays.json --self-test --find-hit --verify-certificate certificates/erdos-142-q6-117-cell-six-deletion-wall/hitting_proof.json
	python3 -I certificates/erdos-142-q6-117-cell-six-deletion-wall/independent_replay.py certificates/erdos-142-q6-117-cell-six-deletion-wall/rays.json certificates/erdos-142-q6-117-cell-six-deletion-wall/hitting_proof.json --self-test
	python3 -I certificates/erdos-142-q6-m7-cellu-restricted-wall/verify.py
	python3 -I certificates/erdos-142-q6-m7-cellu-restricted-wall/independent_replay.py
	python3 -I certificates/erdos-142-q6-m7-deletion-fence/verify.py --self-test
	python3 -I certificates/erdos-142-q6-m7-deletion-fence/independent_replay.py
	python3 -I certificates/erdos-142-q6-m7-orbit-free-selector/verify.py --self-test
	python3 -I certificates/erdos-142-q6-m7-orbit-free-selector/independent_replay.py
	python3 -I certificates/erdos-142-q6-m7-unit-girth-six-wall/verify.py --self-test
	python3 -I certificates/erdos-142-q6-m7-unit-girth-six-wall/independent_replay.py
	python3 -I certificates/erdos-142-q6-m7-unit-k8-deletion-fence/verify.py --self-test
	python3 -I certificates/erdos-142-q6-m7-unit-k8-deletion-fence/independent_replay.py
	python3 -I certificates/erdos-142-q6-m7-k8-microbox-deletion-fence/verify.py --self-test
	python3 -I certificates/erdos-142-q6-m7-k8-microbox-deletion-fence/independent_replay.py
	python3 -I certificates/erdos-142-q6-m7-redesign-torsion-wall/verify.py --self-test
	python3 -I certificates/erdos-142-q6-m7-redesign-torsion-wall/independent_replay.py --self-test
	python3 -I certificates/erdos-142-q4-affine-order4-line-wall/verify.py --self-test
	python3 -I certificates/erdos-142-q7-q8-unit-hypercycle-walls/verify.py --self-test
	python3 -I certificates/erdos-142-q3m-torsion-triangle-wall/verify.py --self-test
	python3 -I certificates/erdos-142-interior-torus-torsion-wall/verify.py --self-test

test:
	python3 -m pytest tests/ -q

# Claim-bound trust gate. Unlike verifier filename discovery, this checks that
# every promoted statement is attached to exact artifact bytes, publication
# text, a semantic replay verdict, and an explicit planted-failure boundary.
check-contracts:
	python3 tools/check_certificate_contracts.py

replay-contracts-fast:
	python3 tools/check_certificate_contracts.py --profile fast

# Requires an 11 GB-class runner because Erdős #979 at 10^12 is the
# claim-bearing slow replay. This is intentionally separate from hosted CI.
replay-contracts-slow:
	python3 tools/check_certificate_contracts.py --profile slow

audit-fast: validate check-views check-book check-graph check-contracts replay-contracts-fast test

audit-slow: check-receipts

# Receipt-drift gate. Slower (~4 min: replays every certificate verify*/check*
# script, incl. fk-square ~2 min) so it is NOT in `test`. Fails if a committed
# receipt disagrees with its own verifier -- the "verifier overwrites its
# receipt on replay" defect the fast checks cannot see. Run before merging any
# change under certificates/. Coverage is PARTIAL: it can only re-derive
# receipts a verifier actually produces (it prints a coverage line, and names
# lanes with receipts but no verifier). Green here means "no receipt on a
# checked lane disagrees with its code", not "every receipt is certified".
check-receipts:
	python3 tools/check_receipt_drift.py --all
