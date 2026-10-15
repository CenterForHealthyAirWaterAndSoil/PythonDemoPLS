#!/usr/bin/env python3
"""Replay provisional VOC indicators and check record/rule integrity (Python 3.10+).

This program does NOT read journal articles, invoke an LLM, validate scientific
judgments, verify source semantics, or re-run the browser-assisted extraction.
It operates on the AI-authored structured records supplied with this pilot.
"""
from __future__ import annotations
import argparse
import copy
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

GATES = ('human_health_analysis','air_route_supported',
         'claim_matches_measured_scope','essential_information_complete')
BOOL_FIELDS = GATES + ('critical_alternative_explanation',
    'controls_adequate_for_narrow_claim','robustness_support','precision_sufficient_for_claim')

def check_inputs(x: dict[str, Any]) -> None:
    for key in BOOL_FIELDS:
        if type(x.get(key)) is not bool:
            raise ValueError(f'{key} must be a JSON boolean')
    if x.get('temporality') not in {'supported','uncertain','contradicted'}:
        raise ValueError('Invalid temporality')
    if x.get('exposure_contrast') not in {'controlled','quasi_experimental','observational'}:
        raise ValueError('Invalid exposure_contrast')

def assign_indicator(x: dict[str, Any]) -> tuple[str,str]:
    check_inputs(x)
    if not all(x[k] for k in GATES):
        return 'Not assessable','R1'
    if x['temporality'] != 'supported':
        return 'Limited','R2'
    if x['critical_alternative_explanation'] or not x['controls_adequate_for_narrow_claim']:
        return 'Limited','R3'
    if (x['exposure_contrast'] in {'controlled','quasi_experimental'}
            and x['robustness_support'] and x['precision_sufficient_for_claim']):
        return 'Stronger','R4'
    return 'Moderate','R5'

def validate_record(r: dict[str, Any], sources: dict, framework: dict) -> list[str]:
    """Structural checks only: a registered pointer is not verified source truth."""
    errors=[]
    try: check_inputs(r['inputs'])
    except (ValueError, KeyError) as e: errors.append(str(e))
    expected=set(framework['hill_domains'])
    if set(r.get('hill',{})) != expected: errors.append('Missing/extra Hill domains')
    ev_ids={e['evidence_id'] for e in r.get('evidence',[])}
    if len(ev_ids)!=len(r.get('evidence',[])): errors.append('Duplicate evidence ID')
    for e in r.get('evidence',[]):
        if e.get('source_id') not in sources: errors.append('Unregistered source: '+str(e.get('source_id')))
        if not e.get('locator','').strip(): errors.append('Missing source locator')
        if not e.get('text','').strip(): errors.append('Missing evidence text')
    for domain,h in r.get('hill',{}).items():
        if h.get('status') not in framework['domain_statuses']: errors.append('Invalid Hill status: '+domain)
        if not h.get('rationale'): errors.append('Missing rationale: '+domain)
        if not h.get('evidence_ids') or not set(h['evidence_ids']).issubset(ev_ids):
            errors.append('Invalid evidence pointer: '+domain)
    return errors

def execute(data_dir: Path, out: Path) -> dict:
    load=lambda n: json.loads((data_dir/n).read_text(encoding='utf-8'))
    records=load('papers.json'); boundaries=load('boundaries.json')
    sources={s['source_id']:s for s in load('sources.json')}; framework=load('framework_v1.json')
    out.mkdir(parents=True,exist_ok=True)
    checks=[]
    def test(name, category, condition, note=''):
        checks.append(dict(test_id=f'T{len(checks)+1:03}',name=name,category=category,
                           passed=bool(condition),note=note))
    rows=[]
    for r in records:
        errors=validate_record(r,sources,framework)
        test(r['paper_id']+' record structure','Record structure',not errors,'; '.join(errors) or 'Nine domains, valid inputs and registered evidence pointers; not source correctness.')
        label,rule=assign_indicator(r['inputs'])
        r['indicator']=label; r['triggered_rule']=rule
        rows.append(dict(paper_id=r['paper_id'],citation=r['short_citation'],role=r['role'],
                         cohort_family=r['cohort_family'],indicator=label,triggered_rule=rule,
                         finding_direction=r['finding']['direction']))
        test(r['paper_id']+' deterministic replay','Deterministic replay',
             all(assign_indicator(copy.deepcopy(r['inputs']))==(label,rule) for _ in range(3)),
             'Identical structured inputs, not repeated AI extraction.')
        for gate in GATES:
            x=copy.deepcopy(r['inputs']);x[gate]=False
            test(r['paper_id']+' '+gate+' absent','Synthetic gate control',assign_indicator(x)==('Not assessable','R1'))
        x=copy.deepcopy(r['inputs']);x['temporality']='uncertain'
        test(r['paper_id']+' temporal information removed','Synthetic gate control',assign_indicator(x)==('Limited','R2'))
        x=copy.deepcopy(r['inputs']);x['temporality']='supported';x['critical_alternative_explanation']=True
        test(r['paper_id']+' critical alternative added','Synthetic gate control',assign_indicator(x)==('Limited','R3'))
        # These fields are not scoring inputs; this tests architecture, not LLM resistance to rhetoric.
        changed=copy.deepcopy(r);changed['title']='X causes Y, certainly';changed['hill']['plausibility']['status']='supportive'
        test(r['paper_id']+' title/background cannot bypass gates','Architecture invariant',assign_indicator(changed['inputs'])==(label,rule),
             'Structured record perturbation only; no altered source was re-read by a model.')
    for b in boundaries:
        lab,ru=assign_indicator(b['inputs'])
        test(b['paper_id']+' abstention','Boundary rule',lab=='Not assessable' and ru=='R1',b['reason'])
    base={k:True for k in BOOL_FIELDS}
    base.update(temporality='supported',critical_alternative_explanation=False,exposure_contrast='controlled')
    test('Controlled well-bounded example','Rule branch',assign_indicator(base)==('Stronger','R4'))
    x=copy.deepcopy(base);x['precision_sufficient_for_claim']=False
    test('Controlled imprecise/null example','Rule branch',assign_indicator(x)==('Moderate','R5'),
         'Null effect direction alone is not proof of equivalence; precision gate is explicit.')
    x=copy.deepcopy(base);x['exposure_contrast']='observational'
    test('Observational contrast does not reach R4','Rule branch',assign_indicator(x)==('Moderate','R5'))
    x=copy.deepcopy(base);x['controls_adequate_for_narrow_claim']=False
    test('Inadequate controls block upgrade','Rule branch',assign_indicator(x)==('Limited','R3'))
    x=copy.deepcopy(base);x['temporality']='contradicted'
    test('Contradicted timing blocks upgrade','Rule branch',assign_indicator(x)==('Limited','R2'))
    damaged=copy.deepcopy(records[0]);damaged['evidence'][0]['source_id']='NONEXISTENT'
    test('Deliberately broken source pointer detected','Negative control',bool(validate_record(damaged,sources,framework)))
    damaged=copy.deepcopy(records[0]);del damaged['hill']['analogy']
    test('Missing Hill domain detected','Negative control',bool(validate_record(damaged,sources,framework)))
    rejected=False
    try:
        x=copy.deepcopy(base);x['air_route_supported']='yes';assign_indicator(x)
    except ValueError: rejected=True
    test('String instead of boolean rejected','Negative control',rejected)
    by_cat={c:dict(passed=sum(t['passed'] for t in checks if t['category']==c),total=sum(t['category']==c for t in checks)) for c in sorted({t['category'] for t in checks})}
    summary=dict(publications=len(records),development=sum(r['role']=='Development' for r in records),
      demonstration=sum(r['role']=='Demonstration' for r in records),
      distinct_study_families=len({r['cohort_family'] for r in records}),hill_domain_records=sum(len(r['hill']) for r in records),
      evidence_records=sum(len(r['evidence']) for r in records),boundary_cases=len(boundaries),
      indicators=dict(Counter(r['indicator'] for r in records)),triggered_rules=dict(Counter(r['triggered_rule'] for r in records)),
      tests_total=len(checks),tests_passed=sum(t['passed'] for t in checks),test_categories=by_cat,
      scientific_accuracy_estimated=False,expert_review_performed=False,independent_model_comparison=False,
      full_source_text_archived=False,source_semantics_automatically_verified=False)
    (out/'rated_papers.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'test_results.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'run_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    with (out/'indicators.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'test_results.txt').write_text('\n'.join(f"{'PASS' if t['passed'] else 'FAIL'} {t['test_id']} {t['name']}" for t in checks)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    if summary['tests_passed']!=summary['tests_total']:raise RuntimeError('One or more computational checks failed')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'results')
    args=parser.parse_args();execute(args.data,args.out)
