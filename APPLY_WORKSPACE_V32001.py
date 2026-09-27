#!/usr/bin/env python3
from pathlib import Path
import argparse
import shutil

p=argparse.ArgumentParser()
p.add_argument('target')
p.add_argument('--payload', required=True)
a=p.parse_args()
target=Path(a.target).expanduser().resolve()
payload=Path(a.payload).expanduser().resolve()
if not target.is_dir():
    raise SystemExit(f'ERROR: target not found: {target}')
if not payload.is_dir():
    raise SystemExit(f'ERROR: payload not found: {payload}')
count=0
for src in payload.rglob('*'):
    if src.is_dir():
        continue
    rel=src.relative_to(payload)
    dst=target/rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src,dst)
    count += 1
print(f'APPLIED_WORKSPACE_V32001_FILES={count}')
for src in sorted(payload.rglob('*')):
    if src.is_file(): print(src.relative_to(payload))
