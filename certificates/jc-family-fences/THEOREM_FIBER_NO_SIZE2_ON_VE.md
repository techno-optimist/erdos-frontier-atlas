# No size-2 fibers on \(V(E)\) (structural fence)

Date: 2026-07-21

**Conditional** on Alpöge's dim-3 Keller counterexample and the annihilator
identities already certified in
[`../jc-anatomy/certify_nonproperness.py`](../jc-anatomy/certify_nonproperness.py)
(\(G_1\), \(\Phi_x\), \(\operatorname{disc}_Y(G_1)=-2916\,t_1^2 E\)).

**Status:** proposed structural fence — machine-reinforced, elementary human
case-split. **Does not auto-close the ledger.** Treat as a reviewable argument
that size-2 is impossible on \(V(E)\), so the fiber spectrum is exactly
\(\{0,1,3\}\) (size **3**), **if** the human steps are accepted.

## Quantity

`jc-fiber-count-spectrum-size` — ledger bracket **[3, 4]** with `2` open.
Observed values: \(\{0,1,3\}\).

## Theorem sketch

**Theorem (proposed).** For every complex \(t\in V(E)\),
\[
\# F^{-1}(t)\in\{0,1\}.
\]
In particular size-2 fibers do not occur. Combined with the certified generic
fiber count \(3\) off \(\{t_1 t_2 E\neq 0\}\) and empty fibers on the cusp curve
\(\gamma\), the fiber-count spectrum of \(F\) is exactly \(\{0,1,3\}\).

### Ingredients (anatomy, already certified)

1. \(G_1(F;y)\equiv 0\): every fiber point has \(y\)-coordinate a root of the
   fiber cubic \(G_1(t;Y)\).
2. \(\Phi_x(F;x)\equiv 0\): every fiber point has \(x\)-coordinate a root of
   \[
   \Phi_x = E\,X^3 + (4-3 t_2 t_3)\,X - 2 t_3.
   \]
3. \(\operatorname{disc}_Y(G_1)=-2916\,t_1^2 E\): on \(V(E)\), \(G_1\) has a
   multiple root over \(\mathbb C\).

### Forced \(x\) on \(V(E)\)

On \(E=0\), \(\Phi_x\) reduces to \((4-3 t_2 t_3)X-2 t_3\).

- If \(d:=4-3 t_2 t_3\neq 0\): unique forced \(x_*=2 t_3/d\).
- If \(d=0\): \(\Phi_x\equiv -2 t_3\). On the cusp
  \(t=(s^2/12,s,4/(3s))\) one has \(t_3\neq 0\), so \(\Phi_x\) is a nonzero
  constant: **no** \(x\) exists, fiber empty (matches the cusp theorem).
- Corner \(t_1=t_2=0\): \(G_1=2Y^3\) (triple root \(0\)), \(d=4\neq 0\), unique
  \(x_*\); fiber \(\le 1\) (realized as \(1\) at anchors).

Thus on \(V(E)\setminus\gamma\) every fiber point shares the same unique \(x_*\),
and \(z\) is uniquely determined by the linear-in-\(z\) system when a solution
exists. So
\[
\# F^{-1}(t)
= \#\{\text{distinct roots \(y\) of \(G_1(t)\) that lift at \(x_*\)}\}.
\]

### Double root never lifts

Write \(t_2=s\). If \(a\) is a multiple root of \(G_1\), then \(G_1'(a)=0\) gives
\[
t_1=\frac{a(s-a)}{3}.
\]
The \((1,2)\)-resultant residual along the line of \(z\)-equations is proportional
to
\[
R_{12}\propto u\bigl(u(y-s)+3 x t_1\bigr),\qquad u=1+y x.
\]
Specialize \(y=a\) and \(t_1=a(s-a)/3\):
\[
u(a-s)+3 x t_1
=(1+a x)(a-s)+x a(s-a)
=(a-s)
\]
**identically in \(x\)** (elementary expansion). Hence
\[
R_{12}\propto u^2(a-s).
\]

- If \(a\neq s\) and \(u\neq 0\): \(R_{12}\neq 0\), no lift.
- If \(u=0\) (i.e. \(x=-1/a\), \(a\neq 0\)): then \(a_1=u^3=0\) and
  \(b_1=-t_1\). Whenever \(t_1\neq 0\), \(p_1\equiv -t_1\neq 0\) for all \(z\), no
  lift.
- Remaining thin loci (\(t_1=0\), \(a=s\); \(t_1=t_2=0\)) are checked directly:
  forced-\(x\) evaluation shows the double/triple root contributes at most one
  point total, never two.

**Corollary.** On \(V(E)\), the multiple root of \(G_1\) never contributes a
second sheet: at most the simple root (if present and distinct) can lift, and
at most once (unique \(x_*\)). Therefore \(\# F^{-1}(t)\le 1\) on
\(V(E)\setminus\gamma\), and \(=0\) on \(\gamma\).

### Shape note (rational base points)

For \(t\in V(E)(\mathbb Q)\), \(\gcd(G_1,G_1')\in\mathbb Q[Y]\) is non-constant,
so the multiple root is rational; Vieta forces the simple root rational too.
Shape `rat_y=1, leftover=2` **cannot occur** for rational \(t\in V(E)\). Size-2
via “one rational \(y\) + irrational \(y\)-lifts” is blocked on rational bases.

### Soft two-\(y\) conjecture upgraded

Prior observation ([`THEOREM_FIBER_TWO_Y_SOFT.md`](THEOREM_FIBER_TWO_Y_SOFT.md)):
when two distinct rational \(y\)-roots exist, lift patterns were always `1+0` or
`0+1` (631 pts). The structural reason: the double root never lifts; only the
simple root can. Pattern `1+1` is impossible.

## What this does **not** claim

- Does **not** auto-update `atlas/jc-crater` ledger brackets.
- Does **not** re-prove anatomy annihilators (imported as hypotheses).
- The \(R_{12}\) identity is elementary algebra (human step), reinforced by dense
  rational specializations in the probe scripts — not a Gröbner / multivariate
  certificate object.
- Root claim remains external / awaiting confirmation.

## Probes / artifacts

| file | role |
|------|------|
| `probe_fiber_no_size2_ve.py` | full sample + identity grid + parametric family |
| `probe_fiber_two_y_lemma.py` | parametric soft-lemma formalization |
| `probe_fiber_size2_push.py` | expanded shape×fiber classification |
| `_tiny_run_core.py` | stdlib-only core (no sibling import) |
| `FIBER_NO_SIZE2_VE.json` | full probe output (replay) |
| `FIBER_NO_SIZE2_VE_CORE.json` | core output (replay) |
| `FIBER_TWO_Y_LEMMA.json` | parametric two-\(y\) output (replay) |
| `FIBER_SIZE2_PUSH.json` | push sample output (replay) |

## Replay

```sh
python3 -I _tiny_run_core.py
python3 -I probe_fiber_two_y_lemma.py
python3 -I probe_fiber_no_size2_ve.py
python3 -I probe_fiber_size2_push.py
```

## Relation to prior samples

| sample | points | hist | size-2 |
|--------|--:|------|--:|
| exact v2 | 249 | {0:10,1:239} | 0 |
| param dense | 467 | {0:10,1:457} | 0 |
| two-\(y\) soft | 631 | {0:12,1:619} | 0 |
| this fence | structural | {0,1} on \(V(E)\) | ruled out |

No size-2 hit in any rational sample. The new content is the **structural**
non-lifting of the double root, not merely a larger sample.
