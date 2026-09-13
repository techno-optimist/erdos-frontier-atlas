# Precise open input for a sparse-square improvement

This file extracts the next mathematical target from `report.md`; it is **not a theorem**.

For some fixed `eta,rho>0`, seek, uniformly for `T^(5/6-rho)<=D<=T^(5/6+rho)`,

\[
\mathcal O_w(T,D)\ll T^{1/3-\eta},
\]

where

\[
\mathcal O_w=2\sum_{d,e\in[D,2D)}\frac{\mu(d)\mu(e)}{de}
\sum_{nd^2\ne me^2}\frac{1}{\sqrt{nm}}
\int w(t/T)W(2\pi nm/t)
 e^{-it\log(nd^2/(me^2))}\,dt.
\]

Take `G(z)=(1-4z^2)exp(z^2)` and `W(x)=(2pi i)^(-1) int_(2) G(z)x^(-z) dz/z`; `w` ranges over a fixed bounded smooth nonnegative high-shell class. Also require uniformity for the fixed interval-truncated Möbius blocks needed in the divisor decomposition. Preserve the signs and the exact kernel.

The full AFE diagonal is `T log(T) Q_D int(w) + O(T/D)`, where

\[
Q_D=\sum_{d,e\in[D,2D)}\mu(d)\mu(e)\frac{(d,e)^2}{d^2e^2}\asymp D^{-1}.
\]

The AFE error costs only `T^(-2/3+eps)(T/D+1)`. Thus the diagonal is `T^(1/6+o(1))` and the error is `T^(-1/2+eps)` at the critical cell.

For `n,m~N<=T^(1/2+eps)`, put the kernel and bounded dyadic amplitudes inside a dimensionless signed sum `R_N`. The off-diagonal block is `2T R_N/(N D^2)`. A sufficient blockwise bound is

\[
|R_N|\ll ND^2T^{-2/3-\eta-\delta}
\]

for an aggregate loss reserve `delta>0`. At `N~sqrt(T),D=T^(5/6)`, the normalized target is `T^(3/2-eta-delta)`, whereas an unsigned very-near-core count has size at least `T^(5/3)`. Hence the positive-counting approach loses a factor at least `T^(1/6+eta)` before reserved losses. The full diagonal scale would correspond to the stronger target `R_N<<ND*T^o(1)`.

A verified composite-square extension of Khan's reciprocity, followed by a bound for its **Möbius-weighted dual-family sum**, is another possible interface. The small published individual error is not itself a bound for that dual term. Neither an out-of-range `17/33` formula nor a `mu(n)` mollifier theorem may be treated as this input.
