# Exact closure of the fifteen-state Hamiltonian-chain residual

Date: 2026-08-19. This is a scratch-only structural theorem package. It is
separate from, and does not mutate, the frozen at-most-fourteen-state package.

## Result

Use the frozen q42 weights

```text
B = 263277 = 441*597,
R = 17640  = 441*40.
```

The at-most-fourteen-state proof leaves only one new blue-acyclic shape at
fifteen states: after relabeling,

```text
0 ->blue 1 ->blue ... ->blue 14 ->blue undefined.
```

**Theorem.** For every strong partial deterministic red completion of this
blue chain, if the weighted Perron root of `W=B A+R C` exceeds `B`, then the
seven-copy product has a nondegenerate active pure-to-pure witness for every
one of the 225 ordered start/target pairs. Consequently this Hamiltonian-chain
residual cannot escape the frozen q42 homogeneous partial-decoder wall.

Together with the separate frozen at-most-fourteen-state structural theorem
and its cyclic-blue lemma, this closes the same wall through fifteen live
states. The physical packet lift and all scope restrictions are unchanged.

## Feedback reduction

Let

```text
P=(I-A)^(-1)=I+A+...+A^14,
Q=P C,
t=B/R=597/40.
```

At a scalar red weight `s`,

```text
I-A-sC = (I-A)(I-sPC).
```

The standard nonnegative M-matrix/next-generation equivalence therefore
gives

```text
rho(A+(40/597)C) > 1  iff  rho(Q) > 597/40.
```

Concretely, row `i` of `Q` is the sum of red-map rows whose sources are
`i,i+1,...,14`. Its row sum is the number of defined red transitions in that
suffix.

If at most fourteen red transitions are defined, every row sum of `Q` is at
most 14, strictly below `t`. Hence an above-`B` table has all fifteen red
transitions defined.

## Exact classification of total red maps

Let `q` be the number of red transitions whose target is not the chain head
zero.

If `q>=2`, use the positive vector

```text
z_0=1,  z_i=77/80 for i>=1.
```

Row zero satisfies

```text
(Qz)_0 <= 13+2*(77/80)=597/40=t,
```

and every later row has at most fourteen terms, while

```text
t*(77/80)=45969/3200 > 14.
```

Thus `Qz<=tz` and `rho(Q)<=t`.

Suppose `q=1` and the unique nonzero target is `j>=2`. Use

```text
z_0=1,
z_j=37/40,
z_i=560/597 for i not in {0,j}.
```

Row zero is exactly `14+37/40=t`. Every ordinary later row is at most 14,
which equals `t*(560/597)`. Row `j` has at most `15-j<=13` terms, strictly
less than `t*(37/40)=22089/1600`. Again `rho(Q)<=t`.

Therefore only sixteen total red maps can be above the threshold:

1. every red transition targets zero;
2. for one selected source `p in {0,...,14}`, `red(p)=1` and every other red
   transition targets zero.

All sixteen maps are strong. In the first case `rho(Q)=15`. In the second
case the Perron root is the large root of

```text
lambda^2-14lambda-14 = 0,  if p=0,
lambda^2-15lambda+1  = 0,  if p>0.
```

At `t=597/40`, the two polynomials equal respectively

```text
-311/1600,  -191/1600.
```

Since `t` lies above the small root, both signs prove that the large Perron
root is strictly above `t`. This establishes an exact if-and-only-if
classification; no floating point or sampling enters it.

## Explicit product words

Use action `B` for a common blue column, `R` for a common red column, and
`U_0` for a unit column selecting one copy at state zero for red while the
other six take blue.

First send the chosen start `s` to zero by a common prefix:

```text
all-red-to-zero map:             R;
p=0:                             empty if s=0, otherwise R;
p=1:                             BR if s=1, otherwise R;
p>=2:                            RR if s=p, otherwise R.
```

The following active cores are then valid:

```text
all-red-to-zero:  U_0 R,       ending pure at 0;
p=0:              U_0,         ending pure at 1;
p=1:              U_0 U_0 R,   ending pure at 0;
p>=2:             U_0 R,       ending pure at 0.
```

For a core ending at zero, append `B^t` to reach target `t`. For `p=0`,
append `R` for target zero or `B^(t-1)` for target `t>=1`.

Every common column has red count zero or seven; every `U_0` column has red
count one. At least one unit column occurs. The words are defined, finish at
one common target, and have length at most 19. Thus they are explicit
nondegenerate seven-multisunflowers for all 3,600 critical-map/start/target
triples.

## Independent exact product replay

The C++ replay constructs all `C(21,7)=116280` seven-copy occupancy
histograms, doubles them by the activity bit to 232,560 product states, and
uses the seventeen exact actions (common blue/red plus one unit-red action per
state). It independently screens all sixteen critical maps and all 225 pairs
per map.

The exact result is

```text
critical maps                       16
ordered pairs                     3600
missing pairs                        0
maximum shortest horizon            18
maximum reached product states    65107
sum of per-map reached maxima    920075
```

This direct graph calculation is redundant with the universal words and uses
no spectral premise.

## Scope and nonclaims

Proved here: only the fifteen-state Hamiltonian blue-chain residual for the
frozen q42 color-homogeneous partial deterministic interface. Combined with
the separately frozen structural package, it closes at most fifteen live
states.

Not proved: an at-most-sixteen-state wall; arbitrary same-count colorings;
physical-symbol-dependent or box-sensitive transitions; state carving;
nondeterminism; unbounded states; a physical potential from packet avoidance;
a new `r_3(N)` bound; or Erdos Problem 142.

## Replay

Windows:

```powershell
.\run.ps1
```

WSL/Linux:

```sh
sh ./run.sh
```

Terminal markers:

```text
PASS_EXACT_FIFTEEN_CHAIN_RESIDUAL_CLOSURE
PASS_EXACT_FIFTEEN_CHAIN_CRITICAL_PRODUCT_SCREEN
PASS_FIFTEEN_STATE_CHAIN_CLOSURE
```
