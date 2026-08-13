#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from _common import CONTROL_REPOS, PASS_SAFETY, append_event, batch_digest, gh_json, gh_repo_absent, load_jsonl, project_root

DELETE_DISPOSITIONS = {'DELETE_REDUNDANT_FORK','PRESERVE_THEN_DELETE','STAR_UPSTREAM_THEN_DELETE','DELETE_ORIGINAL'}


def deletion_eligibility_errors(approval: dict, record: dict | None) -> list[str]:
    errors = []
    if not record:
        return ['repository record missing']
    if approval.get('full_name') in CONTROL_REPOS:
        errors.append('control repository is excluded')
    if approval.get('repo_id') != record.get('repo_id') or (approval.get('full_name') or '').lower() != (record.get('full_name') or '').lower():
        errors.append('approval identity does not match repository record')
    if not approval.get('approved_at') or not approval.get('approved_by'):
        errors.append('approved_at and approved_by required')
    if record.get('safety_status') not in PASS_SAFETY:
        errors.append('fork safety test not passed')
    if record.get('recommended_disposition') not in DELETE_DISPOSITIONS:
        errors.append('record is not in a deletion disposition')
    if record.get('preservation_complete') is False:
        errors.append('preservation dependency incomplete')
    if record.get('star_dependency_complete') is False:
        errors.append('upstream-star dependency incomplete')
    return errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--execute', action='store_true')
    p.add_argument('--confirm-batch')
    args = p.parse_args()
    root = project_root()
    approvals = load_jsonl(root / 'queues' / 'approved_deletions.jsonl')
    records = {r['repo_id']: r for r in load_jsonl(root / 'state' / 'repos.jsonl') if isinstance(r.get('repo_id'), int)}
    digest = batch_digest(approvals) if approvals else 'empty'
    print(f'approved deletion batch: {len(approvals)} targets; digest={digest}')
    bad = []
    for a in approvals:
        errs = deletion_eligibility_errors(a, records.get(a.get('repo_id')))
        if errs: bad.append((a.get('full_name'), errs))
        print(f"DELETE {a.get('repo_id')} {a.get('full_name')}")
    if bad:
        raise SystemExit(f'ineligible deletion approvals: {bad}')
    if not args.execute:
        print('DRY RUN only; pass --execute --confirm-batch DIGEST to mutate')
        return 0
    if args.confirm_batch != digest:
        raise SystemExit('confirmation digest mismatch')
    for a in approvals:
        current = gh_json(f"/repositories/{a['repo_id']}")
        if current['full_name'].lower() != a['full_name'].lower():
            raise SystemExit(f"identity mismatch: {current['full_name']} != {a['full_name']}")
        print(f"EXECUTING DELETE {a['repo_id']} {current['full_name']}")
        gh_json(f"/repos/{current['full_name']}", method='DELETE')
        if not gh_repo_absent(a['repo_id']):
            raise SystemExit(f"post-delete verification failed for {a['repo_id']} {current['full_name']}")
        print(f"VERIFIED ABSENT {a['repo_id']} {current['full_name']}")
        append_event(root / 'state' / 'decisions.jsonl', {
            'event':'DELETE_EXECUTED','repo_id':a['repo_id'],'full_name':current['full_name'],
            'approved_at':a['approved_at'],'approved_by':a['approved_by'],
            'executed_at':datetime.now(timezone.utc).isoformat(),'batch_digest':digest,
        })
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
