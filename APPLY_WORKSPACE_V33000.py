#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('target'); p.add_argument('--payload',required=True); a=p.parse_args()
target=Path(a.target).expanduser().resolve(); payload=Path(a.payload).resolve()
if not target.exists(): raise SystemExit(f'ERROR: target missing: {target}')
if not payload.is_dir(): raise SystemExit(f'ERROR: payload missing: {payload}')
files=[]
for src in sorted(x for x in payload.rglob('*') if x.is_file()):
    rel=src.relative_to(payload); dst=target/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst); files.append(rel.as_posix())
print(f'APPLIED_WORKSPACE_V33000_FILES={len(files)}')
for f in files: print(f)
