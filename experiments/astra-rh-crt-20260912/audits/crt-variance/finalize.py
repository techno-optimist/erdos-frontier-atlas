from pathlib import Path
import json
import subprocess
from fractions import Fraction as F
from math import prod
from audit import rho, terms

ROOT=Path(__file__).resolve().parent
SOURCES='<excluded-tool>/sources.py'
base=['python3',SOURCES,'--ledger',str(ROOT/'sources-ledger.json')]
parent=Path('<excluded-browser-workspace>')
for i in (0,1):
    data=json.loads((parent/f'rh-crt-primary-{i}.json').read_text())
    text=data['text']
    path=ROOT/f'parent-primary-{i}.txt'
    path.write_text(text)
    if i==0:
        anchor=text.find('Haar measure')
        if anchor>=0:
            start=max(0,text.rfind('\n',0,anchor))
            end=text.find('\n\n',anchor)
            if end<0: end=anchor+600
            quote=text[start:end].strip()
            subprocess.run(base+['quote','12','--text',quote,'--from',str(path)],check=True)
            print('Cellarosi-Sinai evidence:',quote[:700])
        else:
            raise RuntimeError('No Haar uniform-measure anchor found')
    else:
        anchor=text.find('Lemma 3.4')
        print('GMR primary-HTML formula excerpt:',text[anchor:anchor+1600])

weighted_checks=0
for P in [(),(2,),(3,),(2,3)]:
    L=prod(P)**2
    for c in [[F(1),F(-1)],[F(2),F(0),F(-3,2),F(1,3)]]:
        left=sum(sum(cj*(int(all((n+j)%(p*p) for p in P))-rho(P)) for j,cj in enumerate(c))**2 for n in range(L))/L
        right=F(0)
        for d,a in terms(P):
            q=d*d
            v=sum(sum(cj*(int((u+j)%q==0)-F(1,q)) for j,cj in enumerate(c))**2 for u in range(q))/q
            right+=a*v
        assert left==right,(P,c,left,right)
        weighted_checks+=1

r_results=json.loads((ROOT/'r-free-results.json').read_text())
summary={
    'squarefree':json.loads((ROOT/'audit-results.json').read_text()),
    'endpoints':json.loads((ROOT/'endpoint-results.json').read_text()),
    'r_free_direct_checks':sum(x['direct_checks'] for x in r_results['results']),
    'r_free_real_checks':sum(x['real_checks'] for x in r_results['results']),
    'weighted_covariance_checks':weighted_checks,
    'authored_scripts':['audit.py','endpoints.py','r-free.py','finalize.py']
}
(ROOT/'verification-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Additional verification:',{k:v for k,v in summary.items() if k not in ('squarefree','endpoints')})
subprocess.run(base+['render','--replace-in',str(ROOT/'audit-report.md')],check=True)
subprocess.run(base+['verify',str(ROOT/'audit-report.md'),'--evidence'],check=True)
