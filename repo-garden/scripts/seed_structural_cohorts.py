#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import date, timedelta
from urllib.parse import urlencode
from _common import atomic_write_jsonl, gh_json, project_root


def cohort_query(day: str, lane: str) -> str:
    d = date.fromisoformat(day)
    if lane == 'level0':
        return f'user:granolacowboy fork:only created:{day} pushed:<{(d + timedelta(days=1)).isoformat()}'
    if lane == 'level1':
        return f'user:granolacowboy fork:only created:{day} pushed:>{day}'
    raise ValueError('lane must be level0 or level1')


def fetch_search(query: str) -> list[dict]:
    items: list[dict] = []
    page = 1
    while True:
        qs = urlencode({'q': query, 'per_page': 100, 'page': page})
        obj = gh_json(f'/search/repositories?{qs}')
        page_items = obj.get('items', [])
        items.extend(page_items)
        if len(items) >= int(obj.get('total_count', len(items))) or not page_items:
            break
        page += 1
    return items


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--date', default='2025-05-24')
    args = p.parse_args()
    root = project_root()
    for lane in ('level0','level1'):
        query = cohort_query(args.date, lane)
        items = fetch_search(query)
        rows = [{
            'repo_id': int(r['id']), 'full_name': r['full_name'],
            'structural_lane': lane.upper(), 'query': query,
            'created_at': r.get('created_at'), 'pushed_at': r.get('pushed_at'),
        } for r in items]
        atomic_write_jsonl(root / 'queues' / f'structural_{lane}_pending.jsonl', rows)
        print(f'{lane}: {len(rows)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
