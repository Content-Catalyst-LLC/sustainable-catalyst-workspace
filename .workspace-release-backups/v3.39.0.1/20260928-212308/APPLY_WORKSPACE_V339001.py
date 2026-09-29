#!/usr/bin/env python3
from pathlib import Path
import shutil, sys, datetime
release=Path(__file__).resolve().parent
repo=Path(sys.argv[1] if len(sys.argv)>1 else Path.home()/"Downloads/sustainable-catalyst-workspace").resolve()
if not (repo/'.git').exists(): raise SystemExit(f'Not a git repository: {repo}')
config=(repo/'backend/app/config.py').read_text()
if '3.39.0' not in config and '3.39.0.1' not in config: raise SystemExit('Workspace v3.39.0 baseline not found')
payload=release/'payload'
files=[p for p in payload.rglob('*') if p.is_file()]
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup=repo/'.workspace-release-backups'/'v3.39.0.1'/stamp
for src in files:
    rel=src.relative_to(payload); dst=repo/rel
    if dst.exists():
        b=backup/rel; b.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(dst,b)
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
print(f'APPLIED_WORKSPACE_V339001_FILES={len(files)}')
print(f'WORKSPACE_V339001_BACKUP={backup}')
print('APPLIED_WORKSPACE_V339001=PASS')
