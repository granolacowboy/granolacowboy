#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import tempfile
from typing import Any, Iterable

CONTROL_REPOS = {
    'granolacowboy/github-star-garden',
    'granolacowboy/github-repo-garden',
    'granolacowboy/granolacowboy',
}
VALID_DISPOSITIONS = {
    'KEEP_ACTIVE','KEEP_ORIGINAL','KEEP_CUSTOM_FORK','DELETE_REDUNDANT_FORK',
    'STAR_UPSTREAM_THEN_DELETE','PRESERVE_THEN_DELETE','ARCHIVE_ORIGINAL',
    'DELETE_ORIGINAL','DEFER'
}
PASS_SAFETY = {'PASS','PASS_LEVEL0','PASS_LEVEL1','PASS_METADATA_FAST_PATH'}


def project_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[1]


def load_jsonl(path: os.PathLike[str] | str) -> list[dict[str, Any]]:
    p = pathlib.Path(path)
    if not p.exists() or p.stat().st_size == 0:
        return []
    rows: list[dict[str, Any]] = []
    for i, raw in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f'{p}:{i}: invalid JSON: {exc}') from exc
        if not isinstance(obj, dict):
            raise ValueError(f'{p}:{i}: expected JSON object')
        rows.append(obj)
    return rows


def atomic_write_jsonl(path: os.PathLike[str] | str, rows: Iterable[dict[str, Any]]) -> None:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=p.name + '.', dir=p.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            for row in rows:
                fh.write(json.dumps(row, sort_keys=True, separators=(',', ':')) + '\n')
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_write_json(path: os.PathLike[str] | str, value: Any) -> None:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=p.name + '.', dir=p.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            json.dump(value, fh, indent=2, sort_keys=True)
            fh.write('\n')
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def batch_digest(rows: Iterable[dict[str, Any]]) -> str:
    identities = sorted(f"{int(r['repo_id'])}:{r['full_name']}" for r in rows)
    payload = ''.join(x + '\n' for x in identities).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def gh_json(endpoint: str, *, method: str = 'GET', paginate: bool = False, fields: dict[str, str] | None = None) -> Any:
    cmd = ['gh', 'api']
    if method != 'GET':
        cmd += ['--method', method]
    if paginate:
        cmd.append('--paginate')
    if fields:
        for k, v in fields.items():
            cmd += ['-f', f'{k}={v}']
    cmd.append(endpoint)
    try:
        proc = subprocess.run(cmd, check=True, text=True, capture_output=True)
    except FileNotFoundError as exc:
        raise RuntimeError('gh CLI is required') from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"gh api failed: {' '.join(cmd)}\n{exc.stderr.strip()}") from exc
    text = proc.stdout.strip()
    if not text:
        return None
    if paginate:
        dec = json.JSONDecoder()
        pos = 0
        values = []
        while pos < len(text):
            while pos < len(text) and text[pos].isspace():
                pos += 1
            if pos >= len(text):
                break
            value, pos = dec.raw_decode(text, pos)
            values.append(value)
        if all(isinstance(v, list) for v in values):
            return [item for page in values for item in page]
        return values
    return json.loads(text)


def append_event(path: pathlib.Path, event: dict[str, Any]) -> None:
    rows = load_jsonl(path)
    rows.append(event)
    atomic_write_jsonl(path, rows)
