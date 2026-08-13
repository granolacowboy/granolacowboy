#!/usr/bin/env python3
from __future__ import annotations

import argparse
from _common import batch_digest, gh_json, load_jsonl, project_root


def star_eligibility_errors(row: dict) -> list[str]:
    errors = []
    if not isinstance(row.get('repo_id'), int) or not row.get('full_name'):
        errors.append('repo_id and full_name required')
    if not row.get('approved_at') or not row.get('approved_by'):
        errors.append('approved_at and approved_by required')
    if '/' not in (row.get('full_name') or ''):
        errors.append('full_name must be owner/name')
    return errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--execute', action='store_true')
    p.add_argument('--confirm-batch')
    args = p.parse_args()
    rows = load_jsonl(project_root() / 'queues' / 'approved_stars.jsonl')
    digest = batch_digest(rows) if rows else 'empty'
    print(f'approved star batch: {len(rows)} targets; digest={digest}')
    errors = [(r.get('full_name'), star_eligibility_errors(r)) for r in rows if star_eligibility_errors(r)]
    if errors:
        raise SystemExit(f'invalid approvals: {errors}')
    for r in rows:
        print(f"STAR {r['repo_id']} {r['full_name']}")
    if not args.execute:
        print('DRY RUN only; pass --execute --confirm-batch DIGEST to mutate')
        return 0
    if args.confirm_batch != digest:
        raise SystemExit('confirmation digest mismatch')
    for r in rows:
        current = gh_json(f"/repositories/{r['repo_id']}")
        if current['full_name'].lower() != r['full_name'].lower():
            raise SystemExit(f"identity mismatch for {r['repo_id']}: {current['full_name']} != {r['full_name']}")
        gh_json(f"/user/starred/{current['full_name']}", method='PUT')
        gh_json(f"/user/starred/{current['full_name']}")
        print(f"VERIFIED STAR {current['full_name']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
