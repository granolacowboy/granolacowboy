#!/usr/bin/env python3
from __future__ import annotations

from _common import PASS_SAFETY

KEEP_RECS = {'KEEP_REFERENCE','KEEP','KEEP_ACTIVE','KEEP_STRATEGIC'}


def derive_queue(row: dict) -> str:
    if not row.get('fork'):
        return row.get('recommended_disposition', 'DEFER')
    if row.get('unique_state'):
        return 'KEEP_CUSTOM_FORK'
    if row.get('safety_status') not in PASS_SAFETY:
        return 'DEFER'
    starred = row.get('canonical_starred')
    if starred is True:
        return 'DELETE_REDUNDANT_FORK'
    if starred is False:
        if row.get('star_garden_recommendation') in KEEP_RECS or row.get('canonical_should_star') is True:
            return 'STAR_UPSTREAM_THEN_DELETE'
        if row.get('canonical_should_star') is False:
            return 'DELETE_REDUNDANT_FORK'
    return 'DEFER'


def main() -> int:
    from _common import atomic_write_jsonl, load_jsonl, project_root
    root = project_root()
    records = load_jsonl(root / 'state' / 'repos.jsonl')
    buckets = {
        'redundant_forks.jsonl': [], 'star_then_delete.jsonl': [],
        'preserve_then_delete.jsonl': [], 'needs_judgment.jsonl': [],
        'original_repo_review.jsonl': []
    }
    for r in records:
        disposition = derive_queue(r)
        out = dict(r)
        out['recommended_disposition'] = disposition
        if disposition == 'DELETE_REDUNDANT_FORK':
            buckets['redundant_forks.jsonl'].append(out)
        elif disposition == 'STAR_UPSTREAM_THEN_DELETE':
            buckets['star_then_delete.jsonl'].append(out)
        elif disposition == 'PRESERVE_THEN_DELETE':
            buckets['preserve_then_delete.jsonl'].append(out)
        elif r.get('fork'):
            buckets['needs_judgment.jsonl'].append(out)
        else:
            buckets['original_repo_review.jsonl'].append(out)
    for name, rows in buckets.items():
        atomic_write_jsonl(root / 'queues' / name, rows)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
