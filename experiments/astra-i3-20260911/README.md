# i=3 slice of P699

Unpromoted. **Not a solution of #699.** Campaign: `GOAL.md`.

Kernel-checked (Lean 4.33.1 Init, axioms `[propext, Quot.sound]`):

- Pascal identity \(j^{\underline{3}}\binom nj = n^{\underline{3}}\binom{n-3}{j-3}\)
- If \(j^{\underline{3}}<\binom n3\) then \(\gcd(\binom n3,\binom nj)\ge 2\)
- If \(n\equiv 3\pmod 4\) then \(\binom n3\) is odd, so that gcd is odd and \(\ge 3\)

Python supplies the size bound on \(8\le n\le 80\) (**1369** pairs, **342** with \(n\equiv 3\pmod 4\)) and finds **no 2-power gcd** through \(n=120\).

The 2-adic residual \(n\not\equiv 3\pmod 4\) is the next crack. \(i\ge 4\) cannot use this size bound (\(2^i\le i!\)).
