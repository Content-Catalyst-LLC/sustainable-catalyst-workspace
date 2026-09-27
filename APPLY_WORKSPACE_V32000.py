#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil
from pathlib import Path

p=argparse.ArgumentParser(description='Apply Sustainable Catalyst Workspace v3.20.0 payload')
p.add_argument('target', help='Workspace repository path')
p.add_argument('--payload', required=True, help='Repository-relative payload directory')
a=p.parse_args()
target=Path(a.target).expanduser().resolve(); payload=Path(a.payload).expanduser().resolve()
if not target.is_dir(): raise SystemExit(f'ERROR: target not found: {target}')
if not (target/'.git').exists(): raise SystemExit(f'ERROR: target is not a git repository: {target}')
if not payload.is_dir(): raise SystemExit(f'ERROR: payload not found: {payload}')
files=[]
for src in sorted(payload.rglob('*')):
    if not src.is_file(): continue
    rel=src.relative_to(payload); dst=target/rel
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst); files.append(rel)
print(f'APPLIED_WORKSPACE_V32000_FILES={len(files)}')
for rel in files: print(rel)
