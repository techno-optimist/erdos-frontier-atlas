#!/usr/bin/env python3
"""Build the research-only connection overlay; never writes production graph/statuses."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PIN = 'adc7f1241b42e322a6451854ab7e4b4c146bf78a'
RELATIONS = {'external_statement_match', 'conditional_derivation', 'candidate', 'blocked_transfer', 'declared_dependency'}
SHARDS = ['root-connections.json', 'swarm/number-theory.json', 'swarm/combinatorics.json', 'swarm/analytic-audit.json']
# Independent reviews of an existing edge are provenance, not extra discoveries.
DUPLICATES = {
    'swarm/analytic-audit.json': {0: 'root-08', 1: 'root-09', 3: 'root-12', 4: 'root-13'},
    'swarm/number-theory.json': {11: 'root-05', 12: 'root-06', 19: 'root-16', 20: 'root-02',
                               21: 'root-12', 22: 'root-13', 24: 'root-22', 25: 'root-03',
                               26: 'root-04', 30: 'root-17', 37: 'root-21', 46: 'root-07'},
    'swarm/combinatorics.json': {5: 'root-01', 8: 'root-20', 46: 'root-19'},
}
ROOT_PROBLEMS = {'root-08': ['P969'], 'root-09': ['P969'], 'root-10': ['P969'],
                 'root-11': ['P969'], 'root-14': ['P3', 'P142'], 'root-23': ['P969']}


def build():
    catalogue = json.loads((HERE / 'catalogue.json').read_text())
    families = {'F' + f['family_id']: f for f in catalogue['families']}
    stubs = json.loads((REPO / 'atlas/stubs.json').read_text())
    problems = {'P' + str(p['id']): p for p in stubs['problems']}
    edges, reviews = [], []
    for shard in SHARDS:
        data = json.loads((HERE / shard).read_text())
        pin = data.get('source_pin', data.get('source_commit', data.get('commit')))
        if pin is not None and pin != PIN:
            raise ValueError(f'{shard}: wrong source pin {pin}')
        for i, original in enumerate(data['edges'] + data.get('family_dependencies', [])):
            if i in DUPLICATES.get(shard, {}):
                reviews.append({'edge_id': DUPLICATES[shard][i], 'review_file': shard, 'review_edge_index': i,
                                'source_edge': original,
                                'scope': 'Additional model review or overlapping statement mapping; not a new connection.'})
                continue
            e = dict(original)
            if e['relation'] == 'declared_dependency':
                e['target_id'] = e.pop('target_family')
                e['missing_hypotheses'] = ['Dependency proof and necessity not independently audited.']
            f = str(e['source_family'])
            e['source_family'] = f if f.startswith('F') else 'F' + f.zfill(3)
            if e['source_family'] not in families:
                raise ValueError(f'{shard}: unknown family {f}')
            relation = e['relation']
            if relation == 'scoped_bound_improvement':
                e['relation_detail'] = relation
                relation = 'external_statement_match'
            if relation == 'method_candidate':
                e['relation_detail'] = relation
                relation = 'candidate'
            if relation == 'conditional_composition':
                e['relation_detail'] = relation
                relation = 'conditional_derivation'
            if relation not in RELATIONS:
                raise ValueError(f'{shard}: unknown relation {relation}')
            e['relation'] = relation
            e['edge_id'] = e.get('edge_id', Path(shard).stem + '-' + str(i + 1).zfill(2))
            e['origin'] = {'file': shard, 'edge_index': i}
            e['external_proof_verification'] = 'NOT_RUN'
            e['canonical_status_effect'] = 'NONE'
            for key in ('target_id', 'scope', 'missing_hypotheses', 'source_urls'):
                if key not in e:
                    raise ValueError(f'{shard}: missing {key}')
            if isinstance(e['missing_hypotheses'], str):
                e['missing_hypotheses'] = [e['missing_hypotheses']]
            if not isinstance(e['missing_hypotheses'], list) or not isinstance(e['source_urls'], list):
                raise ValueError(f'{shard}: list fields expected')
            if not e['source_urls']:
                raise ValueError(f'{shard}: no source')
            for url in e['source_urls']:
                if 'github.com/openai/math/' in url and PIN not in url:
                    raise ValueError(f'{shard}: unpinned source {url}')
            if re.fullmatch(r'P\d+', e['target_id']) and e['target_id'] not in problems:
                raise ValueError(f'{shard}: unknown problem {e["target_id"]}')
            if e['edge_id'] in ROOT_PROBLEMS:
                e['related_problem_ids'] = ROOT_PROBLEMS[e['edge_id']]
            edges.append(e)
    by_id = {e['edge_id']: e for e in edges}
    for review in reviews:
        base = by_id[review['edge_id']]
        source = review['source_edge']['source_family']
        source = source if str(source).startswith('F') else 'F' + str(source).zfill(3)
        if source != base['source_family']:
            raise ValueError('Duplicate mapping source changed: ' + review['review_file'])
        # Analytic review routes methods to their associated P969 problem.
        if review['review_file'] != 'swarm/analytic-audit.json' and review['source_edge']['target_id'] != base['target_id']:
            raise ValueError('Duplicate mapping target changed: ' + review['review_file'])
    ids = [e['edge_id'] for e in edges]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate edge IDs')
    nodes = []
    node_ids = sorted({e['source_family'] for e in edges} | {e['target_id'] for e in edges} | {v for e in edges for v in e.get('additional_inputs', []) if v in families})
    for node in node_ids:
        if node in families:
            nodes.append({'id': node, 'kind': 'external_family', 'title': families[node]['title'], 'source_commit': PIN})
        elif node in problems:
            nodes.append({'id': node, 'kind': 'atlas_problem', 'url': problems[node]['erdos_url']})
        else:
            nodes.append({'id': node, 'kind': 'research_interface'})
    return {
        'schema': 'efa-research-connection-overlay-v1',
        'source_commit': PIN,
        'atlas_baseline_commit': 'a21acb5',
        'scope': 'Scoped statement matches, conditional informal derivations, candidates and blocked transfers. Not a proof or canonical status ledger.',
        'external_proof_verification': 'NOT_RUN',
        'canonical_status_changes': False,
        'coverage': {'catalogue_family_titles_scanned': len(families),
                     'atlas_problem_records': len(problems),
                     'atlas_records_with_statement': sum(bool(p.get('statement')) for p in problems.values()),
                     'limitation': 'Targeted source inspection; not an exhaustive theorem audit. Link-only records and uninspected proofs limit recall. Edge count is not solved-problem count.'},
        'counts': {'nodes': len(nodes), 'edges': len(edges),
                   'source_families': len({e['source_family'] for e in edges}),
                   'atlas_problem_targets': len({e['target_id'] for e in edges if re.fullmatch(r'P\d+', e['target_id'])}),
                   'by_relation': dict(sorted(Counter(e['relation'] for e in edges).items()))},
        'supporting_reviews_and_duplicate_mappings': reviews,
        'nodes': nodes,
        'edges': edges,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if committed overlay differs from sources.')
    parser.add_argument('--target', help='Print incoming edges for P969, F076, or a research interface.')
    args = parser.parse_args()
    data = build()
    encoded = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
    destination = HERE / 'connections.json'
    if args.target:
        selected = [e for e in data['edges'] if e['target_id'] == args.target or args.target in e.get('related_problem_ids', [])]
        print(json.dumps(selected, indent=2, ensure_ascii=False))
    elif args.check:
        if not destination.exists() or destination.read_text() != encoded:
            raise SystemExit('Connection overlay is stale; run build_connections.py')
        print('Connection overlay matches validated source shards: ' + json.dumps(data['counts']))
    else:
        destination.write_text(encoded)
        print(json.dumps(data['counts']))


if __name__ == '__main__':
    main()
