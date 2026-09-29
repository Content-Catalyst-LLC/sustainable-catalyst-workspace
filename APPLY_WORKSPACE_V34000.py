#!/usr/bin/env python3
from pathlib import Path
import shutil,sys,datetime
release=Path(__file__).resolve().parent; target=Path(sys.argv[1] if len(sys.argv)>1 else Path.home()/"Downloads/sustainable-catalyst-workspace").expanduser().resolve(); payload=release/'payload'
if not (target/'.git').exists(): raise SystemExit(f'ERROR: not a git repository: {target}')
config=(target/'backend/app/config.py').read_text(errors='replace')
if '3.39.0.1' not in config and '3.40.0' not in config: raise SystemExit('ERROR: v3.39.0.1 baseline marker missing')
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S'); backup=target/'.workspace-release-backups/v3.40.0'/stamp; count=0
for src in sorted(payload.rglob('*')):
 if not src.is_file(): continue
 rel=src.relative_to(payload); dst=target/rel
 if dst.exists():
  b=backup/rel; b.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(dst,b)
 dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst); count+=1
print(f'APPLIED_WORKSPACE_V34000_FILES={count}'); print(f'WORKSPACE_V34000_BACKUP={backup}'); print('APPLIED_WORKSPACE_V34000=PASS')
