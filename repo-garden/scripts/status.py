#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from _common import load_jsonl, project_root


def main() -> int:
    root = project_root()
    repos = load_jsonl(root / 'state' / 'repos.jsonl')
    dispositions = Counter((r.get('current_disposition') or r.get('recommended_disposition') or 'UNSET') for r in repos)
    safety = Counter(r.get('safety_status','UNSET') for r in repos)
    out = {
        'repo_records': len(repos),
        'forks': sum(bool(r.get('fork')) for r in repos),
        'dispositions': dict(sorted(dispositions.items())),
        'safety': dict(sorted(safety.items())),
        'approved_stars': len(load_jsonl(root / 'queues' / 'approved_stars.jsonl')),
        'approved_deletions': len(load_jsonl(root / 'queues' / 'approved_deletions.jsonl')),
        'needs_judgment': len(load_jsonl(root / 'queues' / 'needs_judgment.jsonl')),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
