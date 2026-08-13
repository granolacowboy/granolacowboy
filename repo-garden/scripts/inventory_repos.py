#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from _common import atomic_write_jsonl, gh_json, load_jsonl, project_root

LIVE_FIELDS = (
    'id','full_name','fork','private','visibility','archived','disabled','default_branch',
    'created_at','updated_at','pushed_at','size','license','topics','description','has_pages',
    'open_issues_count'
)


def merge_inventory(existing: list[dict], live: list[dict]) -> list[dict]:
    by_id = {int(r['repo_id']): dict(r) for r in existing if isinstance(r.get('repo_id'), int)}
    out = []
    for src in live:
        rid = int(src['id'])
        row = by_id.get(rid, {'repo_id': rid, 'current_disposition': 'DEFER'})
        row['repo_id'] = rid
        for key in LIVE_FIELDS:
            if key == 'id':
                continue
            if key in src:
                row[key] = src[key]
        row['inventory_seen_at'] = datetime.now(timezone.utc).isoformat()
        out.append(row)
    return sorted(out, key=lambda r: (r.get('full_name') or '').lower())


def main() -> int:
    root = project_root()
    existing = load_jsonl(root / 'state' / 'repos.jsonl')
    live = gh_json('/user/repos?affiliation=owner&per_page=100&sort=full_name', paginate=True)
    merged = merge_inventory(existing, live)
    atomic_write_jsonl(root / 'state' / 'repos.jsonl', merged)
    print(f'inventoried {len(merged)} owned repositories')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
