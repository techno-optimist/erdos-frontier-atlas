# Exact Fourier transforms below $`n\log n`$

The following describes the scope of the Lean formalization related to the following accompanying paper(s):

- [Finite tensor savings and exact Fourier circuits](../../preprints/Finite-tensor-savings-and-exact-Fourier-circuits-September-25-2026/main.pdf)
- [An explicit power saving for the exact discrete Fourier transform](../../preprints/An-explicit-power-saving-for-the-exact-discrete-Fourier-transform-September-25-2026/main.pdf)

## Scope

The formalized result gives exact discrete Fourier transforms with arbitrarily small normalized circuit cost along an unbounded sequence of lengths. For every $c>0$ and every cutoff $N_0\ge2$, some $n\ge N_0$ has a circuit computing the unnormalized DFT with fewer than $cn\log_2 n$ gates. Addition, subtraction, and multiplication by a predetermined complex scalar each cost one gate; diagonal scalings are charged. The result is subsequential, with no all-length, bounded-coefficient, conditioning, or bit-complexity claim.

A separate uniform formalization gives fixed deterministic programs for every positive length $n$, computing the canonical discrete Fourier transform and the full convolution of two length-$n$ complex vectors exactly. Their work is $O(n(\log n)^{1-10^{-13}})=o(n\log n)$, including root-order selection and scalar preparation. The chosen root of unity is supplied; the model permits exact complex arithmetic and unrestricted coefficients, while integer values and indices remain polynomially bounded in $n$. The synthesis appendix's extraction, search, and printer uniformization is outside these selected statements.

## Comparator links

| Result | Comparator statement |
| --- | --- |
| Subsequential savings for exact Fourier circuits | [ExactFourier.lean](../ComparatorChallenges/ExactFourier.lean) |
| Uniform exact DFT and convolution with a power saving | [UniformFourier.lean](../ComparatorChallenges/UniformFourier.lean) |
