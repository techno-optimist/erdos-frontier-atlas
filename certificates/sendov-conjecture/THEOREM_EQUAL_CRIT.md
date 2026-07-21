# Theorem (equal-critical-point family — no Sendov CE)

**Statement.** Let \(n\ge 2\), \(\beta\in\mathbb C\), and \(c\in\mathbb C\). Define
\[
p'(z)=(z-c)^{n-1},\qquad p(z)=\int_\beta^z (w-c)^{n-1}\,dw
=\frac1n\Big((z-c)^n-(\beta-c)^n\Big).
\]
Then \(p(\beta)=0\), every critical point is at \(c\), and the Sendov radius at \(\beta\) is
\(r=|\beta-c|\). The roots of \(p\) are
\[
z_k=c+(\beta-c)\,e^{2\pi i k/n},\qquad k=0,\dots,n-1.
\]

**Claim.** This family admits **no** Sendov counterexample: it is impossible to have
both \(r>1\) and \(\max_k|z_k|\le 1\).

**Proof.** Suppose \(r=|\beta-c|>1\). The points \(z_k\) lie on the circle of radius \(r\)
centered at \(c\). If every \(|z_k|\le 1\), that circle would lie in the closed unit disk,
which requires \(|c|+r\le 1\). Then \(r\le 1-|c|\le 1\), contradicting \(r>1\).
Hence some root has modulus \(>1\). ∎

**Check.** `results/wave5_equal_crit_theorem.json` records a dense numeric scan
with 0 violations; `results/wave5_left_ray_mp.json` multiprecision-checks the
left ray \(\beta=1\), \(c=1-R\) (so \(r=R\)) for many \(n,R\).

**Replay.** Covered by `verify.py` leg 14.
