#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from urllib.parse import quote

from _common import PASS_SAFETY, atomic_write_json, atomic_write_jsonl, gh_json, project_root
from analyze_forks import classify_fork_evidence, metadata_fast_path_eligible
from seed_structural_cohorts import cohort_query, fetch_search


def star_set_complete(observed: int, expected: int | None) -> bool:
    return expected is not None and observed == expected


def disposition_for(row: dict) -> str:
    if row.get('unique_state'):
        return 'KEEP_CUSTOM_FORK'
    if row.get('safety_status') not in PASS_SAFETY:
        return 'DEFER'
    if row.get('canonical_starred') is True:
        return 'DELETE_REDUNDANT_FORK'
    return 'DEFER'


def read_checkpoint(root):
    path = root / 'state' / 'checkpoint.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


def analyze_candidate(summary: dict, star_ids: set[int]) -> dict:
    name = summary['full_name']
    row = {
        'repo_id': int(summary['id']), 'full_name': name, 'fork': True,
        'created_at': summary.get('created_at'), 'pushed_at': summary.get('pushed_at'),
        'current_disposition': 'DEFER',
    }
    try:
        meta = gh_json(f'/repos/{name}')
    except RuntimeError as exc:
        row.update({'safety_status':'DEFER','unique_state':True,'reason':f'OWNED_REPO_METADATA_ERROR: {exc}'})
        return row
    parent, source = meta.get('parent'), meta.get('source')
    if not parent:
        row.update({'safety_status':'DEFER','unique_state':True,'reason':'ORPHAN_OR_INACCESSIBLE_PARENT'})
        return row
    canonical = source or parent
    row.update({
        'parent_repo_id':int(parent['id']),'parent_full_name':parent['full_name'],
        'source_repo_id':int(canonical['id']),'source_full_name':canonical['full_name'],
        'canonical_repo_id':int(canonical['id']),'canonical_full_name':canonical['full_name'],
        'canonical_starred':int(canonical['id']) in star_ids,
        'has_pages':bool(meta.get('has_pages')),'open_issues_count':int(meta.get('open_issues_count') or 0),
        'has_discussions':bool(meta.get('has_discussions')),
    })
    if metadata_fast_path_eligible(meta):
        row.update({
            'safety_status':'PASS_METADATA_FAST_PATH','unique_state':False,
            'reason':'NO_POST_FORK_PUSH_AND_NO_ACCOUNT_SIDE_ACTIVITY_SIGNALS','confidence':0.985,
        })
    else:
        branch = meta['default_branch']
        parent_branch = parent.get('default_branch') or branch
        try:
            compare = gh_json(f"/repos/{parent['full_name']}/compare/{quote(parent_branch, safe='')}...{quote('granolacowboy:'+branch, safe=':')}")
            refs = [r['ref'] for r in gh_json(f'/repos/{name}/git/refs')]
            row.update(classify_fork_evidence(compare=compare, refs=refs, default_branch=branch, source_accessible=True))
            row['confidence'] = 0.995 if row.get('safety_status') == 'PASS_LEVEL1' else 0.7
        except RuntimeError as exc:
            row.update({'safety_status':'DEFER','unique_state':True,'reason':f'LEVEL1_COMPARE_ERROR: {exc}','confidence':0.4})
    row['recommended_disposition'] = disposition_for(row)
    return row


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--date',default='2025-05-24')
    args=p.parse_args()
    root=project_root()
    checkpoint=read_checkpoint(root)
    expected_stars=checkpoint.get('live_star_count_from_star_garden')
    stars=gh_json('/users/granolacowboy/starred?per_page=100',paginate=True)
    star_rows=[{'repo_id':int(r['id']),'full_name':r['full_name']} for r in stars]
    star_ids={r['repo_id'] for r in star_rows}
    atomic_write_jsonl(root/'state'/'live_stars.jsonl',star_rows)
    query=cohort_query(args.date,'level0')
    candidates=fetch_search(query)
    rows=[]
    for i,summary in enumerate(candidates,1):
        rows.append(analyze_candidate(summary,star_ids))
        if i % 25 == 0: print(f'analyzed {i}/{len(candidates)}')
    safe_starred=[r for r in rows if r.get('recommended_disposition')=='DELETE_REDUNDANT_FORK']
    safe_nonstarred=[r for r in rows if r.get('safety_status') in PASS_SAFETY and not r.get('canonical_starred')]
    anomalies=[r for r in rows if r.get('safety_status') not in PASS_SAFETY]
    atomic_write_jsonl(root/'state'/f'sweep_a_{args.date}_level0.jsonl',rows)
    atomic_write_jsonl(root/'queues'/'redundant_forks_level0_unapproved.jsonl',safe_starred)
    atomic_write_jsonl(root/'queues'/'nonstarred_forks_value_review.jsonl',safe_nonstarred)
    atomic_write_jsonl(root/'queues'/'level0_anomalies.jsonl',anomalies)
    complete=star_set_complete(len(star_rows),expected_stars)
    checkpoint.update({
        'live_star_identity_set_materialized':complete,'live_star_materialized_count':len(star_rows),
        'live_star_expected_count':expected_stars,
        'live_star_scope_note':'public user-star endpoint; treated complete only when count matches Star Garden live count',
        'may_24_level0_materialized':len(rows),'may_24_level0_safe_star_overlap':len(safe_starred),
        'may_24_level0_safe_nonstarred':len(safe_nonstarred),'may_24_level0_anomalies':len(anomalies),
        'last_updated':datetime.now(timezone.utc).isoformat(),
    })
    atomic_write_json(root/'state'/'checkpoint.json',checkpoint)
    report=f'''# Automated Sweep A — {args.date}\n\n- Live stars materialized: {len(star_rows)} (expected {expected_stars}; complete={complete})\n- Level-0 structural candidates: {len(rows)}\n- Safety-passed + canonical currently starred: {len(safe_starred)}\n- Safety-passed + canonical not in live-star set: {len(safe_nonstarred)}\n- Escalated anomalies: {len(anomalies)}\n\nNo stars, unstars, archives, or repository deletions were performed. All output queues are unapproved analysis queues.\n'''
    (root/'reports'/'AUTO_SWEEP_A.md').write_text(report,encoding='utf-8')
    print(report)
    return 0

if __name__=='__main__': raise SystemExit(main())
