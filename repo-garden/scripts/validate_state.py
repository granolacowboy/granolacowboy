#!/usr/bin/env python3
from __future__ import annotations

import json
from _common import CONTROL_REPOS, VALID_DISPOSITIONS, load_jsonl, project_root


def validate_approval_rows(rows: list[dict], *, kind: str) -> list[str]:
    errors: list[str] = []
    seen_ids: set[int] = set()
    for idx, row in enumerate(rows, 1):
        prefix = f'{kind}[{idx}]'
        rid = row.get('repo_id')
        name = row.get('full_name')
        if not isinstance(rid, int) or not name:
            errors.append(f'{prefix}: approval requires repo_id and full_name')
            continue
        if rid in seen_ids:
            errors.append(f'{prefix}: duplicate repo_id {rid}')
        seen_ids.add(rid)
        if kind == 'deletion' and name in CONTROL_REPOS:
            errors.append(f'{prefix}: control repository may never be auto-deleted: {name}')
        if not row.get('approved_at') or not row.get('approved_by'):
            errors.append(f'{prefix}: approval requires approved_at and approved_by evidence')
    return errors


def main() -> int:
    root = project_root()
    errors: list[str] = []
    repo_rows = load_jsonl(root / 'state' / 'repos.jsonl')
    ids: set[int] = set()
    names: set[str] = set()
    for i, row in enumerate(repo_rows, 1):
        rid, name = row.get('repo_id'), row.get('full_name')
        if not isinstance(rid, int) or not name:
            errors.append(f'repos[{i}]: missing stable repo_id/full_name')
            continue
        if rid in ids: errors.append(f'repos[{i}]: duplicate repo_id {rid}')
        if name in names: errors.append(f'repos[{i}]: duplicate full_name {name}')
        ids.add(rid); names.add(name)
        disp = row.get('current_disposition') or row.get('recommended_disposition')
        if disp and disp not in VALID_DISPOSITIONS:
            errors.append(f'repos[{i}]: invalid disposition {disp}')
    errors += validate_approval_rows(load_jsonl(root / 'queues' / 'approved_stars.jsonl'), kind='star')
    errors += validate_approval_rows(load_jsonl(root / 'queues' / 'approved_deletions.jsonl'), kind='deletion')
    if errors:
        print(json.dumps({'ok': False, 'errors': errors}, indent=2))
        return 1
    print(json.dumps({'ok': True, 'repo_records': len(repo_rows)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
