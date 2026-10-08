#!/usr/bin/env python3
"""Replay retained upstream metadata and graph overlap; no network or proof execution."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
OLD='adc7f1241b42e322a6451854ab7e4b4c146bf78a'
NEW='fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
FORMAL_FAMILIES={'FourierLLogL':'075','HadwigerCounterexample':'157','LogspaceEquality':'103',
 'OneTapeSpace':'137','StableCoordinateFour':'049','UniformFourier':'130',
 'CharacterVarietiesAllSeamsSupport':'027','CartierChartCompactnessSupport':'066',
 'SurfaceConeCandidateSupport':'195','TraceIdealTransportSupport':'301','HoneycombBridgeMassSupport':'237'}
SUPPORT={'CharacterVarietiesAllSeamsSupport','CartierChartCompactnessSupport','SurfaceConeCandidateSupport',
         'TraceIdealTransportSupport','HoneycombBridgeMassSupport'}
LOCAL_PINS={'catalogue.json':'b730c71c30eaeb6b337f0de7a384d0092cd0e0d830933bae128b362aedadc9ad',
 'connections.json':'68c8261b0c539e4de52b1727f1d0a42cf6a414f732446f3048895947213db77e',
 'swarm/number-theory.json':'b7b9996d6f795e3a5b6b1226b6e6bcb4cdaf3373d9248c7ca46564f11083b3ef'}


def need(ok,why):
    if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def enc(x):return (json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def decode(raw):
    def pairs(rows):
        d={}
        for k,v in rows:need(k not in d,'duplicate JSON key');d[k]=v
        return d
    def reject(_):raise ValueError('nonfinite JSON')
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=reject)
def read(name):
    p=Path(name);need(not p.is_absolute() and all(x not in ('','.','..') for x in name.split('/')),'contained path')
    p=HERE/p;need(not any(q.is_symlink() for q in (p,*p.parents)) and p.is_file() and p.stat().st_size<4*1024*1024,'bounded local file')
    return p.read_bytes()

def catalogue(text):
    headers=list(re.finditer(r'^\*\*(\d{3})\. (.*?)\*\*(.*)$',text,re.M));families=[];blocks={}
    for i,h in enumerate(headers):
        end=headers[i+1].start() if i+1<len(headers) else len(text)
        blocks[h[1]]=text[h.start():end]
        body=text[h.end():end];lean=re.search(r'\[Lean\]\((lean/docs/\d{3}\.md)\)',h[3])
        clean=lambda s:html.unescape(re.sub(r'<[^>]+>','',s))
        papers=[{'title':clean(t),'path':p} for t,p in re.findall(r'&emsp;\[(.*?)\]\((preprints/[^)]+)\)',body)]
        need(papers,'nonempty family')
        families.append({'family_id':h[1],'title':clean(h[2]).rstrip('.'),'lean_scope_path':lean[1] if lean else None,'manuscripts':papers})
    ids=[f['family_id'] for f in families];paths=[p['path'] for f in families for p in f['manuscripts']]
    need(len(set(ids))==len(ids) and len(set(paths))==len(paths),'unique catalogue identities')
    return families,blocks,{'families':len(ids),'manuscripts':len(paths),
                           'families_with_catalogue_lean_link':sum(f['lean_scope_path'] is not None for f in families)}

def calculate():
    sources=decode(read('sources.json'))
    need(sources['old_commit']==OLD and sources['new_commit']==NEW,'fixed source commits')
    names=set()
    for row in sources['files']:
        need(row['path'] not in names and type(row['bytes']) is int,'unique typed source rows');names.add(row['path'])
        raw=read(row['path']);need(sha(raw)==row['sha256'] and len(raw)==row['bytes'],'retained source identity')
    local={}
    for name,pin in LOCAL_PINS.items():
        raw=(BASE/name).read_bytes();need(sha(raw)==pin,'historical local artifact remains unchanged');local[name]=decode(raw)
    old,ob,oc=catalogue(read('raw/old-contents.md.txt').decode());new,nb,nc=catalogue(read('raw/new-contents.md.txt').decode())
    need(old==local['catalogue.json']['families'] and oc==local['catalogue.json']['counts'],'exact original catalogue')
    need(oc=={'families':372,'manuscripts':722,'families_with_catalogue_lean_link':235},'old counts')
    need(nc=={'families':372,'manuscripts':719,'families_with_catalogue_lean_link':242},'new counts')
    need(list(ob)==list(nb),'same family IDs');changed=[k for k in ob if ob[k]!=nb[k]]
    editions=[];withdrawals=[];title_changes=[]
    bynew={f['family_id']:f for f in new}
    for a in old:
        b=bynew[a['family_id']]
        if a['title']!=b['title']:title_changes.append({'family_id':a['family_id'],'old':a['title'],'new':b['title']})
        oldpaths={p['path'] for p in a['manuscripts']};newpaths={p['path'] for p in b['manuscripts']}
        added=[p for p in b['manuscripts'] if p['path'] not in oldpaths]
        for p in a['manuscripts']:
            if p['path'] in newpaths:continue
            match=[q for q in added if q['title']==p['title']]
            need(len(match)<=1,'unambiguous edition pairing')
            row={'family_id':a['family_id'],'title':p['title'],'old_path':p['path']}
            if match:
                row['new_path']=match[0]['path'];added.remove(match[0])
                repair=a['family_id'] in {'034','036','056','232','233','341','342','376'} or p['title'].startswith('Exact Birch')
                row['publisher_history_category']='repair_or_correction' if repair else 'reference_and_version_update'
                editions.append(row)
            else:withdrawals.append(row)
        need(not added,'no unpaired new manuscript')
    need(len(editions)==27 and len(withdrawals)==3 and {r['family_id'] for r in withdrawals}=={'032'},'edition/withdrawal counts')
    need(sum(r['publisher_history_category']=='repair_or_correction' for r in editions)==14,'publisher history repair count')
    history=read('raw/history.md.txt').decode()
    need('## October 7, 2026' in history and '14 other manuscripts' in history and '13 additional manuscripts' in history
         and '300 / 719' in history,'publisher history counts and date')
    for row in withdrawals:
        # Match only the notice heading; normalize its typographic en dash.
        key=row['title'].replace('–','-')
        matching=[n for n in range(1,4) if key in
                  read('raw/withdrawal-'+str(n)+'.md.txt').decode().splitlines()[0].replace('–','-')]
        need(len(matching)==1,'withdrawal exact title join')
        n=matching[0];text=read('raw/withdrawal-'+str(n)+'.md.txt').decode()
        need('Withdrawn on October 6, 2026' in text and OLD in text,'explicit dated archived notice')
        row['notice']='raw/withdrawal-'+str(n)+'.md.txt'
        row['meaning']='withdrawn proof; mathematical statement not established false'
    trees={}
    for version in ('old','new'):
        root=decode(read('raw/'+version+'-tree.json'));view=decode(read('raw/'+version+'-root-tree.json'));pre=decode(read('raw/'+version+'-preprints-tree.json'))
        need(root['truncated'] is False and pre['truncated'] is False and view['truncated'] is False,'complete nonrecursive Git trees')
        need(root['tree']==view['tree'] and view['sha']==(OLD if version=='old' else NEW),'commit-resolved and exact-tree views agree')
        need(next(x['sha'] for x in root['tree'] if x['path']=='preprints' and x['type']=='tree')==pre['sha'],'root-to-preprint tree link')
        need(all(x['type']=='tree' for x in pre['tree']),'preprint directory inventory')
        trees[version]={x['path']:x['sha'] for x in pre['tree']}
    ot,nt=trees['old'],trees['new'];added=sorted(set(nt)-set(ot));removed=sorted(set(ot)-set(nt));modified=sorted(n for n in ot.keys()&nt.keys() if ot[n]!=nt[n])
    need(not removed and len(added)==27 and len(modified)==3 and len(ot)==722 and len(nt)==749,'complete edition directory inventory')
    need(set(added)=={r['new_path'].split('/')[1] for r in editions}
         and set(modified)=={r['old_path'].split('/')[1] for r in withdrawals},'tree changes exactly match catalogue/withdrawals')
    configs=lambda name:set(re.findall(r'^    - comparator_config: ComparatorChallenges/(\w+)\.json$',read(name).decode(),re.M))
    oldconfigs=configs('raw/old-formalization.yaml');newconfigs=configs('raw/new-formalization.yaml')
    need(not oldconfigs-newconfigs and newconfigs-oldconfigs==set(FORMAL_FAMILIES),'eleven configuration additions')
    text=read('raw/comparator-readme.md.txt').decode();support=set(re.findall(r'^- `(\w+)\.json`:',text,re.M))
    need(support==SUPPORT,'explicit supporting-only classification')
    formal=[{'family_id':FORMAL_FAMILIES[n],'comparator_config':'lean/ComparatorChallenges/'+n+'.json',
             'publisher_scope':'supporting_result_only' if n in SUPPORT else 'additional_main_result_formalization',
             'local_comparator_run':False} for n in sorted(FORMAL_FAMILIES)]
    affected={'F'+k for k in changed}|{'F'+v for v in FORMAL_FAMILIES.values()}
    graph=local['connections.json'];edges=[]
    for e in graph['edges']:
        touched={e.get('source_family'),e.get('target_id')}|set(e.get('additional_inputs',[]))
        if touched&affected:
            need(e['relation']=='blocked_transfer','no silently promoted graph edge')
            row={k:e[k] for k in ('edge_id','source_family','target_id','relation','scope','missing_hypotheses')}
            row['current_annotation']='New formalization metadata does not discharge the separate transfer hypotheses; no local Comparator run.'
            if e['source_family']=='F130':
                row['current_annotation']='New scope separately reports all-length exact DFT/convolution in ideal complex arithmetic. The historical all-length-absence premise is superseded at that source-statement level. Finite-precision/error control and the P969 analytic bridge remain unestablished.'
                row['new_scope_path']='lean/docs/130.md';row['new_scope_sha256']=sha(read('raw/new-scope-130.md.txt'))
            edges.append(row)
    need({e['edge_id'] for e in edges}=={'combinatorics-57','combinatorics-58','analytic-audit-18'},'exact affected edge inventory')
    need(not any(n['id']=='F032' for n in graph['nodes']),'withdrawn family not in graph')
    oldscope=read('raw/old-scope-130.md.txt').decode();newscope=read('raw/new-scope-130.md.txt').decode()
    need('A separate uniform formalization' not in oldscope and 'A separate uniform formalization' in newscope
         and 'every positive length' in newscope and 'unrestricted coefficients' in newscope,'F130 explicit added scope')
    commit=decode(read('raw/commit.json'))
    need(commit['sha']==NEW and OLD in [p['sha'] for p in commit['parents']]
         and commit['tree']['sha']==decode(read('raw/new-tree.json'))['sha'],'commit/tree/parent identity')
    oldcommit=decode(read('raw/old-commit.json'))
    need(oldcommit['sha']==OLD and oldcommit['tree']['sha']==decode(read('raw/old-tree.json'))['sha'],'old commit/tree identity')
    return {'schema':'openai-math-source-update/v2','old_commit':OLD,'new_commit':NEW,
      'new_commit_utc':commit['committer']['date'],'history_heading_date':'2026-10-07','withdrawal_notice_date':'2026-10-06',
      'old_catalogue_counts':oc,'new_catalogue_counts':nc,'changed_catalogue_families':changed,
      'changed_family_titles':title_changes,'withdrawals':withdrawals,'new_editions':editions,
      'publisher_reported_repair_or_correction_count':14,'publisher_reported_reference_and_version_count':13,
      'preprint_trees':{'old_directories':len(ot),'new_directories':len(nt),'new_edition_directories':added,
        'modified_withdrawn_directories':modified,'removed_old_directories':removed,'unchanged_old_directory_count':len(ot)-len(modified)},
      'formalization_additions':formal,'publisher_reported_top_line_formalized':300,'publisher_reported_total_manuscripts':719,
      'affected_graph_edges':edges,'withdrawn_family_graph_edges':0,
      'historical_withdrawn_paper_review':'swarm/number-theory.json: F032 abstract_and_intro record',
      'historical_local_artifacts_sha256':LOCAL_PINS,
      'scope':{'current_catalogue_is_not_local_proof_verification':True,'external_lean_or_comparator_executed':False,
       'historical_graph_changed':False,'canonical_problem_status_changed':False,
       'all_theorems_or_transitive_proof_dependencies_audited':False,'private_or_native_data_included':False,
       'edition_classification':'publisher history and metadata; no repaired proof independently adjudicated'}}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
    need(a.write!=a.check,'choose --write or --check');result=calculate()
    if a.write:
        with (HERE/'update.json').open('xb') as f:f.write(enc(result))
    else:
        need(enc(decode(read('update.json')))==enc(result),'typed exact update replay')
        manifest=decode(read('manifest.json'))
        for r in manifest['artifacts']:
            raw=read(r['path']);need(type(r['bytes']) is int and len(raw)==r['bytes'] and sha(raw)==r['sha256'],'manifest leaf identity')
    print(json.dumps({'status':'passed','old_manuscripts':722,'new_manuscripts':719,'withdrawals':3,'new_editions':27,
                      'affected_graph_edges':len(result['affected_graph_edges']),'proofs_checked':0},sort_keys=True))

if __name__=='__main__':main()
