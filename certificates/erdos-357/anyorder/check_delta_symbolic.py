import sympy as s
k,d,e,n,h=s.symbols('k d eps eta h',positive=True)
T=h*(h+1)/2; M=h*k-d; L=(s.Rational(1,2)-n)*k
lhs=T*((1+e)*k**2+k/2)-M*L-M*(M-1)/2
rhs=(T*e+h*n)*k**2+(h+s.Rational(1,2)-n)*d*k-d**2/2+(T+h)*k/2-d/2
print("T*Smax - M*(1/2-eta)k - M(M-1)/2  minus  Astra's expansion =", s.simplify(s.expand(lhs-rhs)))
