#!/usr/bin/env python3
"""Read pinned Lean sources without executing external Lean or shell code.
This is a lexical import scanner, not Lean dependency elaboration or proof checking.
"""
import argparse, concurrent.futures, hashlib, json, re, urllib.request
from pathlib import Path
PIN='adc7f1241b42e322a6451854ab7e4b4c146bf78a'

def strip_comments(s):
    out=[];i=0;depth=0;string=False
    while i<len(s):
        if depth:
            if s.startswith('/-',i):depth+=1;i+=2
            elif s.startswith('-/',i):depth-=1;i+=2
            else:
                if s[i]=='\n':out.append('\n')
                i+=1
        elif string:
            out.append(' ' if s[i]!='\n' else '\n')
            if s[i]=='\\' and i+1<len(s):out.append(' ');i+=2
            else:
                if s[i]=='"':string=False
                i+=1
        elif s.startswith('/-',i):depth=1;i+=2
        elif s.startswith('--',i):
            j=s.find('\n',i);i=len(s) if j<0 else j
        elif s[i]=='"':string=True;out.append(' ');i+=1
        else:out.append(s[i]);i+=1
    return ''.join(out)

def inspect(text):
    clean=strip_comments(text)
    imports=[]
    for line in clean.splitlines():
        m=re.match(r'\s*(?:(?:public|private)\s+)?(?:meta\s+)?import\s+(.+)',line)
        if m:imports.extend(x for x in m.group(1).split() if re.fullmatch(r'[A-Za-z_][\w.]*',x))
    flags=[]
    pattern=r'\b(?:axiom|sorry|sorryAx|admit|unsafe|implemented_by|extern|native_decide|run_tac|run_elab|run_cmd|elab|macro)\b|#(?:eval|exec)|\binitialize\b'
    for n,line in enumerate(clean.splitlines(),1):
        if re.search(pattern,line):flags.append({'line':n,'text':text.splitlines()[n-1].strip()})
    return imports,flags

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--output',required=True);ap.add_argument('--limit',type=int,default=2000);ap.add_argument('--entry',default='OAI.NumberTheory.DirichletL.Nonvanishing');a=ap.parse_args()
    root=Path(a.cache);root.mkdir(parents=True,exist_ok=True);seen={};frontier=[a.entry];external=set();rounds=[]
    def fetch(m):
        path='lean/'+m.replace('.','/')+'.lean';url=f'https://raw.githubusercontent.com/openai/math/{PIN}/{path}';dst=root/path
        try:
            if dst.exists():raw=dst.read_bytes();cached=True
            else:
                raw=urllib.request.urlopen(url,timeout=30).read();dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw);cached=False
            text=raw.decode();imports,flags=inspect(text)
            return {'module':m,'path':path,'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'imports':imports,'lexical_flags':flags,'from_cache':cached}
        except Exception as e:return {'module':m,'path':path,'url':url,'error':str(e)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        while frontier and len(seen)<a.limit:
            current=sorted(set(frontier)-set(seen))[:a.limit-len(seen)]
            if not current:break
            results=list(pool.map(fetch,current));nexts=set(frontier)-set(current)-set(seen)
            for r in results:
                seen[r['module']]=r
                for m in r.get('imports',[]):
                    if m.startswith('OAI.'):nexts.add(m)
                    else:external.add(m)
            frontier=sorted(nexts-set(seen));rounds.append({'round':len(rounds),'new':len(results),'total':len(seen),'pending':len(frontier)})
            print(json.dumps(rounds[-1]),flush=True)
    obj={'pin':PIN,'entry':a.entry,'method':'lexical_import_closure_without_execution','limit':a.limit,'complete_internal_closure':not frontier and not any('error' in r for r in seen.values()),'pending':frontier,'external_import_boundary':sorted(external),'rounds':rounds,'files':sorted(seen.values(),key=lambda r:r['path'])}
    Path(a.output).write_text(json.dumps(obj,indent=2)+'\n')
    print(json.dumps({'files':len(seen),'bytes':sum(r.get('bytes',0) for r in seen.values()),'errors':sum('error' in r for r in seen.values()),'flags':sum(len(r.get('lexical_flags',[])) for r in seen.values()),'complete':obj['complete_internal_closure']}),flush=True)
if __name__=='__main__':main()
