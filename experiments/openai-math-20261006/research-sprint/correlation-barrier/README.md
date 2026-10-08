# A quantitative correlation barrier for growing windows

Graph attachment: `P969`; research interface `method:fixed-window-mobius-variance`.
This is an informal theorem and proof about bounded sequences, independent of
OpenAI's external claims. The finite probe is an illustration, not verification
of the infinite probabilistic existence argument. No novelty claim is made.

## The theorem

For any fixed c in (0,1], there exists a sequence a(n) in {-1,0,1} such that:

1. Its mean is zero and its mean square is c in the Cesaro limit.
2. For every A>0,

       max_(1<=h<=X) |sum_(n<=X) a(n)a(n+h)| <<_A X/(log X)^A.

3. For every fixed pair of positive-slope integer affine forms
   L_1(n)=un+v, L_2(n)=wn+z, with u,w>=1, v,z>=0 and uz-vw != 0,

       |sum_(n<=X) a(L_1(n))a(L_2(n))| <<_(A,L_1,L_2) X/(log X)^A

   for every A>0.
4. Nevertheless, for every fixed theta in (0,1), putting H=floor(X^theta),

       limsup_(X->infinity) [1/(X H)] sum_(n<=X)
           |sum_(h=1..H) a(n+h)|^2 = infinity.

In particular every fixed-H variance tends to cH, but no positive power-window
variance O(H) follows even from the uniform, faster-than-every-logarithm
pair-correlation estimate in (2). The same sequence works for every theta.
Setting c=1/zeta(2) matches the Mobius diagonal density as well.

The sequence is not asserted multiplicative. This is a counterexample to an
inference from the displayed statistical estimates alone, not a counterexample
to a theorem about Mobius or Liouville with additional arithmetic hypotheses.
It does not refute F007 or any OpenAI manuscript.

## Proof

### 1. A random background with simultaneous cancellation

Take independent variables epsilon_n with probabilities c/2,c/2,1-c for values
1,-1,0. For fixed N and 1<=h<=N, define
S_h(N)=sum_(n=1..N) epsilon_n epsilon_(n+h). Its expectation is zero.
Changing one epsilon coordinate changes at most two summands, each by at most
two, hence changes S_h(N) by at most four. There are at most 2N coordinates.
The bounded-differences inequality therefore gives

    P(|S_h(N)| >= t) <= 2 exp(-t^2/(16N)).

A union bound over h<=N and t=N^(3/4) gives a summable bound
`2N exp(-sqrt(N)/16)`. Borel-Cantelli shows that with probability one,
all sufficiently large N obey max_(h<=N)|S_h(N)| <= N^(3/4).

For any fixed pair L_1,L_2 in (3), at most one index n has L_1(n)=L_2(n),
so the expectation of the corresponding sum is O(1). Each random coordinate
again occurs in at most two summands, and only O_(L_1,L_2)(N) coordinates
are involved. The same concentration argument gives O(N^(3/4)) almost surely
for that fixed pair. There are countably many integer pairs of forms, so
intersect their probability-one events. Intersect also the probability-one
strong laws for epsilon_n and epsilon_n^2. Fix one realization in that event.

The concentration theorem is the classical bounded-differences inequality;
see McDiarmid, [On the method of bounded differences](https://doi.org/10.1017/CBO9781107359949.008)
and the statement in Warnke's [primary research paper](https://arxiv.org/abs/1212.5796).
This application, the modification below and the window calculation are supplied
here. No assertion of a new concentration theorem is intended.

### 2. Sparse, long intervals of ones

For k>=1 put

    N_k = 2^(4^k),       L_k = 2^(4^k-2^k),
    D = union_k [N_k, N_k+L_k-1] intersect the integers.

Define a(n)=1 on D and a(n)=epsilon_n elsewhere. Let
f(T)=T*2^(-sqrt(log_2 T)). For T large enough f is increasing.
If N_k<=T<N_(k+1), the geometric domination of the earlier lengths gives

    # (D intersect [1,T]) <= sum_(j<=k)L_j <= 2L_k <= 2f(T).

The finitely many initial values can be absorbed in a constant. Thus D has
density zero, and in fact its count is O_A(T/(log T)^A) for every fixed A.
The mean and mean-square limits are unchanged.

For h<=N, at most `2 # (D intersect [1,2N])` products epsilon_n epsilon_(n+h)
can change, by at most two each. Uniformly in those h,

    |sum a(n)a(n+h)| <= N^(3/4) + 4 # (D intersect [1,2N]).

This proves (2), since both terms are O_A(N/(log N)^A).
For fixed positive-slope forms, injectivity of each form bounds the number
of changed products by `2 # (D intersect [1,CN+C])` for a fixed C.
The same estimate proves (3). The constants here may depend on the forms.

### 3. Polynomial windows see the planted intervals

Take X_k=2N_k and H_k=floor(X_k^theta). For every fixed theta<1,
H_k/L_k tends to zero. There are exactly L_k-H_k+1 starting indices n whose
entire window n+1,...,n+H_k lies in the kth planted interval. Each has sum H_k.
All these starting indices lie between 1 and X_k for large k. Hence

    [1/(X_k H_k)] sum_(n<=X_k) |sum_(h<=H_k) a(n+h)|^2
      >= (L_k-H_k+1) H_k / X_k
      ~ (H_k/2) 2^(-2^k) -> infinity,

because log_2 H_k = theta*4^k + O(1), which dominates 2^k.
This proves (4) simultaneously for every theta in (0,1): after the single
sequence was fixed, the displayed deterministic comparison holds for each theta.

For fixed H, expanding the square gives cH from the H diagonal terms;
each of the finitely many off-diagonal averages vanishes by (2). This completes
the claimed contrast of quantifiers. The uncentered energy is the one used
in the fixed-window Mobius interface; the sequence's mean tends to zero.

## What this tells the RH lane

A uniform bound delta(X) on the off-diagonal averages appearing in the window
square expansion yields
a generic off-diagonal upper bound O(H^2 delta(X)) in the averaged energy.
To make this o(H) one needs H delta(X)->0, or additional cancellation when
summing over shifts. Any fixed logarithmic saving, and even the faster decay
above, can fail this condition for polynomial H.

Thus a usable upgrade to F007 must supply either a sufficiently strong aggregate
shift estimate or arithmetic structure that rules out this sort of sparse
coherent interval. Merely deriving more fixed-form correlations does not resolve
that obligation. Square frequencies and the zeta weight in the actual P969 mixed
moment remain further requirements; this example concerns a simpler prerequisite.

## Finite reproducible illustration

`finite_probe.py` uses a fully specified SHA-256 sign recipe and plants the k=2
interval at 65,536 of length 4,096. It computes exact integer correlations and
window energies through X=131,072, checks the contained-window lower bound,
and checks that the H=1,024 energy exceeds 24H on average. It also includes
small brute-force cross-checks and rejects a deliberately corrupted receipt.
The hash-generated background is not claimed to be the probability-one infinite
realization in the theorem. Its measurements prove only this finite example.

Run `python3 finite_probe.py --check receipt.json` from this directory.
The checker does not write artifacts. The separate `--emit` mode refuses to
overwrite an existing receipt.
