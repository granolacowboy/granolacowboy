#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
from _common import atomic_write_jsonl, gh_json, load_jsonl, project_root

STAR_GARDEN = 'granolacowboy/github-star-garden'


def _decode_contents_file(path: str) -> str:
    obj = gh_json(f'/repos/{STAR_GARDEN}/contents/{path}')
    return base64.b64decode(obj['content']).decode('utf-8')


def _load_remote_jsonl(path: str) -> list[dict]:
    text = _decode_contents_file(path)
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def reconcile_record(row: dict, live_star_by_id: dict[int, dict], sg_by_id: dict[int, dict]) -> dict:
    out = dict(row)
    cid = out.get('canonical_repo_id') or out.get('source_repo_id') or out.get('parent_repo_id')
    if isinstance(cid, str) and cid.isdigit():
        cid = int(cid)
    star = live_star_by_id.get(cid) if isinstance(cid, int) else None
    if star:
        out['canonical_starred'] = True
        out['canonical_repo_id'] = int(star['id'])
        out['canonical_full_name'] = star['full_name']
    elif isinstance(cid, int):
        out['canonical_starred'] = False
    else:
        wanted = out.get('canonical_full_name') or out.get('source_full_name') or out.get('parent_full_name')
        by_name = {v['full_name'].lower(): v for v in live_star_by_id.values()}
        star = by_name.get((wanted or '').lower())
        out['canonical_starred'] = bool(star)
        if star:
            out['canonical_repo_id'] = int(star['id'])
            out['canonical_full_name'] = star['full_name']
    sg = sg_by_id.get(out.get('canonical_repo_id') or cid)
    if sg:
        out['star_garden_recommendation'] = sg.get('recommendation')
        out['star_garden_category'] = sg.get('primary_category')
        out['star_garden_confidence'] = sg.get('confidence')
        if sg.get('canonical_successor'):
            out['star_garden_canonical_successor'] = sg['canonical_successor']
    return out


def main() -> int:
    root = project_root()
    stars = gh_json('/user/starred?per_page=100', paginate=True)
    live_by_id = {int(r['id']): {'id': int(r['id']), 'full_name': r['full_name']} for r in stars}
    atomic_write_jsonl(root / 'state' / 'live_stars.jsonl', live_by_id.values())
    sg_rows = _load_remote_jsonl('state/repos.jsonl')
    sg_by_id = {int(r['repo_id']): r for r in sg_rows if isinstance(r.get('repo_id'), int)}
    records = load_jsonl(root / 'state' / 'repos.jsonl')
    reconciled = [reconcile_record(r, live_by_id, sg_by_id) for r in records]
    atomic_write_jsonl(root / 'state' / 'repos.jsonl', reconciled)
    print(f'reconciled {len(records)} owned repos against {len(live_by_id)} live stars and {len(sg_by_id)} Star Garden records')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
