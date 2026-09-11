# i=3 slice of P699

Unpromoted. **Not a solution of #699.** Campaign: `GOAL.md`.

Kernel-checked (Lean 4.33.1 Init, axioms `[propext, Quot.sound]`):

- Pascal identity \(j^{\underline{3}}\binom nj = n^{\underline{3}}\binom{n-3}{j-3}\)
- If \(j^{\underline{3}}<\binom n3\) then \(\gcd(\binom n3,\binom nj)\ge 2\)
- If \(n\equiv 3\pmod 4\) then \(\binom n3\) is odd, so that gcd is odd and \(\ge 3\)

- If \(d\mid\binom n3\) and \(\gcd(d,j!)=1\) then \(d\mid\binom nj\) (`cancel_coprime_fac`)

Python supplies the size bound on \(8\le n\le 80\) (**1369** pairs, **342** with \(n\equiv 3\pmod 4\)). Odd part of every gcd \(\ge 3\) through \(n=200\). The only \(o\mid j^{\underline 3}\) hits through \(n=1500\) are (10,5), (16,7), (65,15).

\(i\ge 4\) cannot use the size bound (\(2^i\le i!\)). See `residual.md`.
