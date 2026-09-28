"""briefcaselib: proved reductions as exact operators (stdlib only, Python 3).

The briefcase carries operators, not tables. An operator is a proved reduction turned into
exact code. It takes one instance of an open problem, decides it, and can emit a certificate
that a separate verifier rechecks with elementary arithmetic. Where a reduction cuts an open
slice down to a thin residual, atlas/residuals.json records:
- the residual as a membership predicate;
- how far it has been searched, and the replay command;
- the first members nobody has searched yet.

  nt.py         exact number theory. Primality is proven below 3.3e24 (deterministic
                Miller-Rabin) and Baillie-PSW above, with the line marked. Also factoring
                (Pollard-Brent), CRT, Kummer carries, and smooth/rough splits.
  p699.py       Erdős #699 for every i >= 3, from positional localization. `row(n, i)` decides
                every j in (i, n/2]; `certify_row` and `verify_row` make the decision checkable.
                The theorem is experiments/claude-699-general-i-20260928/README.md.
  residuals.py  the residual ledger: load, membership, exact decision, and the frontier.

Entry points: tools/briefcase.py (command line) and tools/briefcase.html (the same row decider
in the browser, with BigInt).

To add an operator:
1. Put the proof in a note under experiments/.
2. Add a module with a decide function and a certificate/verifier pair.
3. Test it against brute force in tests/.
4. If the reduction leaves a residual, add a record to atlas/residuals.json that names the
   operator, the searched bound and the replay command.

Nothing in the briefcase reads or writes a problem status.
"""
from . import nt, p699, residuals

__all__ = ["nt", "p699", "residuals"]
