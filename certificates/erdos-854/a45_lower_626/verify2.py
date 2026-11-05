# independent verifier: own sieve, trial division, stdlib only; checks the first gap-624 witness at 197#
ps=[p for p in range(2,300) if all(p%q for q in range(2,int(p**.5)+1))][:45]
assert ps[-1]==197
x=3555155923304286400743553058952003425931002006480365103818928470764905612981393
t=624
unc=[i for i in range(1,t) if all((x+i)%p for p in ps)]
ends=all(x%p for p in ps) and all((x+t)%p for p in ps)
print('interior uncovered:',unc,'| endpoints coprime:',ends,'| len(P)=',len(ps))
print('x=',x)
