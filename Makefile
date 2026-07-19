# Erdős Frontier Atlas — release-kit targets (EFA-DR1)
#
#   make hello-frontier      the 10-minute quickstart: replay a DRAT certificate
#                            (+ negative control), re-verify a witness certificate,
#                            read one gap-map entry with its confidence class.
#                            Needs only git + cc + python3.
#   make state-of-frontier   regenerate views/state_of_frontier.md from the data
#   make check-views         fail if views/state_of_frontier.md is stale
#   make validate            gap-map validator (dependency-free) + full atlas
#                            integrity check (needs: pip install -r requirements-dev.lock)
#   make verify-certs        replay every fast in-repo certificate verifier
#   make test                pytest over tests/

.PHONY: hello-frontier state-of-frontier check-views validate verify-certs test

hello-frontier:
	bash scripts/hello_frontier.sh

state-of-frontier:
	python3 tools/state_of_frontier.py

check-views:
	python3 tools/state_of_frontier.py --check

validate:
	python3 tools/validate_gap_map.py
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

test:
	python3 -m pytest tests/ -q
