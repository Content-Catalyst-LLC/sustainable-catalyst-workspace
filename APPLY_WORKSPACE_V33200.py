#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, shutil
ap=argparse.ArgumentParser(); ap.add_argument('target'); ap.add_argument('--payload',required=True); a=ap.parse_args()
target=Path(a.target).resolve(); payload=Path(a.payload).resolve()
if not (target/'.git').is_dir(): raise SystemExit(f'ERROR: git repository not found: {target}')
if not payload.is_dir(): raise SystemExit(f'ERROR: payload not found: {payload}')
count=0
for src in sorted(payload.rglob('*')):
    if not src.is_file(): continue
    rel=src.relative_to(payload); dst=target/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst); count+=1
print(f'APPLIED_WORKSPACE_V33200_FILES={count}')
