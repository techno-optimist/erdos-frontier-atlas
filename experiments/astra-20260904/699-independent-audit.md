# Quick independent audit of the proposed P699 strip argument

Conditional verdict: I see no flaw in the p-adic/divisibility/size comparison,
provided the external EEES theorem really has the stated hypotheses and its
exceptional pairs are checked separately. I did not retrieve that theorem or
the list of twelve exceptions during this quick side audit; this is NOT a
certification of the complete P699 theorem.

Assume i>=2, i<j, n=2j+d, 1<=d<=q-i, where q is the smallest prime strictly
larger than i. Let p>=i be a prime divisor of binom(n,i), absent from binom(n,j),
and let a=v_p(binom(n,i))>=1.

1. If p>i, i! has p-valuation zero and the i consecutive numerator factors
   contain at most one multiple of p. Thus there is t in [0,i-1] with
   p^a | n-t. If p=i (necessarily i is prime), v_p(i!)=1; the unique numerator
   multiple then has valuation a+1. In either case M=p^(a+1_{p=i}) gives
   n mod M=t<i. This needs a>=1; primes with a=0 are irrelevant to V.

2. Since p does not divide binom(n,j), Kummer gives no base-p carry when adding
   j and n-j. In particular, for r=j mod M and s=(n-j) mod M, the low digits add
   without an outgoing carry, so r+s=n mod M=t<i.

3. Because n-j=j+d, M divides d+r-s. Also |d+r-s|<=d+i-1. For p>i this is
   <=q-1<p<=M. For the potentially overlooked p=i case, M>=i^2 and Bertrand's
   postulate gives q<2i<=i^2 (valid also at i=2), so the same strict bound holds.
   Consequently d+r-s=0, i.e. s=r+d, and 2r+d<i.

4. Put h=ceil((i-d)/2). Again q<2i implies 1<=d<i, hence 1<=h and 2h<=i<j.
   The previous inequality gives 0<=r<h. The numerator of binom(j,h) contains
   j-r, divisible by M. Since h<i<=p, the denominator h! is coprime to p.
   Therefore p^a divides binom(j,h); in the p=i case one actually obtains an
   extra factor p. Multiplying over distinct noncommon primes gives W|binom(j,h).

5. Vandermonde gives binom(j,h)^2 < binom(2j,2h): its central summand is the
   left side, and there are other positive summands since 1<=h<j. Since
   2h<=i<j, binom(2j,2h)<=binom(2j,i)<=binom(n,i).

Thus if no common prime >=i exists, V=W<=binom(j,h) implies V^2<binom(n,i),
contradicting the quoted EEES inequality binom(n,i)<V^2 for nonexceptional pairs.
The remaining independent obligations are the exact external inequality's
scope, the definition of V (prime powers, not just squarefree radical), and
explicit elimination or direct checking of every exceptional pair lying in
this strip. Do not call the full theorem proved before those are supplied.
