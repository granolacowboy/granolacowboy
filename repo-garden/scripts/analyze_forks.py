#!/usr/bin/env python3
from __future__ import annotations

import argparse
from urllib.parse import quote
from _common import PASS_SAFETY, atomic_write_jsonl, gh_json, load_jsonl, project_root


def classify_fork_evidence(*, compare: dict, refs: list[str], default_branch: str, source_accessible: bool) -> dict:
    if not source_accessible:
        return {'safety_status':'DEFER','unique_state':True,'reason':'SOURCE_INACCESSIBLE'}
    ahead = int(compare.get('ahead_by', 0))
    default_ref = f'refs/heads/{default_branch}'
    extra_refs = sorted(r for r in refs if r != default_ref)
    if ahead > 0:
        return {'safety_status':'DEFER','unique_state':True,'reason':'UNIQUE_DEFAULT_BRANCH_COMMITS','ahead_by':ahead,'extra_refs':extra_refs}
    if extra_refs:
        return {'safety_status':'DEFER','unique_state':True,'reason':'EXTRA_BRANCH_OR_TAG_REFS','ahead_by':ahead,'extra_refs':extra_refs}
    return {'safety_status':'PASS_LEVEL1','unique_state':False,'ahead_by':ahead,'behind_by':int(compare.get('behind_by',0)),'extra_refs':[]}


def analyze_one(row: dict) -> dict:
    out = dict(row)
    name = out['full_name']
    meta = gh_json(f'/repos/{name}')
    parent = meta.get('parent')
    source = meta.get('source')
    if not meta.get('fork') or not parent:
        return out
    out.update({
        'fork': True,
        'parent_full_name': parent['full_name'],
        'parent_repo_id': int(parent['id']),
        'source_full_name': (source or parent)['full_name'],
        'source_repo_id': int((source or parent)['id']),
        'canonical_full_name': (source or parent)['full_name'],
        'canonical_repo_id': int((source or parent)['id']),
    })
    branch = meta['default_branch']
    parent_branch = parent.get('default_branch') or branch
    head = f"granolacowboy:{branch}"
    try:
        compare = gh_json(f"/repos/{parent['full_name']}/compare/{quote(parent_branch, safe='')}...{quote(head, safe=':')}")
        refs_obj = gh_json(f'/repos/{name}/git/refs')
        refs = [r['ref'] for r in refs_obj]
        evidence = classify_fork_evidence(compare=compare, refs=refs, default_branch=branch, source_accessible=True)
    except RuntimeError as exc:
        evidence = {'safety_status':'DEFER','unique_state':True,'reason':f'API_COMPARE_OR_REF_ERROR: {exc}'}
    out.update(evidence)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', action='append', help='owner/name; repeatable. Default: forks not safety-passed')
    parser.add_argument('--limit', type=int, default=100)
    args = parser.parse_args()
    root = project_root()
    rows = load_jsonl(root / 'state' / 'repos.jsonl')
    wanted = set(args.repo or [])
    count = 0
    result = []
    for row in rows:
        should = row.get('fork') and row.get('safety_status') not in PASS_SAFETY
        if wanted:
            should = row.get('full_name') in wanted
        if should and count < args.limit:
            row = analyze_one(row)
            count += 1
        result.append(row)
    atomic_write_jsonl(root / 'state' / 'repos.jsonl', result)
    print(f'analyzed {count} forks')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
