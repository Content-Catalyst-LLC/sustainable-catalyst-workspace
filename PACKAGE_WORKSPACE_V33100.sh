#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$(pwd)}"; OUT="${2:-$HOME/Downloads}"
[[ -f "$ROOT/backend/neural-runtime/service.py" ]] || { echo "ERROR: run against Workspace repository root" >&2; exit 1; }
python3 "$ROOT/VALIDATE_WORKSPACE_V33100.py" "$ROOT"
mkdir -p "$OUT"
python3 - "$ROOT" "$OUT" <<'PY'
from pathlib import Path
import sys, zipfile
root=Path(sys.argv[1]); out=Path(sys.argv[2])
def zdir(src,dst):
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob('*')):
            if p.is_file() and '/.git/' not in str(p): z.write(p,p.relative_to(src))
zdir(root/'backend',out/'sustainable-catalyst-workspace-backend-v3.31.0.zip')
zdir(root/'wordpress'/'sustainable-catalyst-workspace',out/'sustainable-catalyst-workspace-v3.31.0-wordpress-plugin.zip')
PY
echo "PASS: Workspace v3.31.0 package helpers generated"
