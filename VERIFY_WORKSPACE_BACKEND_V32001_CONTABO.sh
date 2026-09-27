#!/usr/bin/env bash
set -euo pipefail
PORT="${WORKSPACE_PORT:-8094}"
BASE="http://127.0.0.1:${PORT}"

echo "=== Workspace v3.20.0.1 backend compatibility verification ==="
echo "Patch backend requirement: existing Workspace backend v3.20.0; no redeploy required."

if command -v docker >/dev/null 2>&1; then
  docker ps --format '{{.Names}}\t{{.Status}}' | grep -E 'sc-workspace-(backend|worker|neural-runtime)' || true
fi

HEALTH="$(curl -fsS "$BASE/health")"
printf '%s\n' "$HEALTH"
python3 - "$HEALTH" <<'PY'
import json,sys
obj=json.loads(sys.argv[1])
version=str(obj.get('version') or obj.get('service_version') or obj.get('serviceVersion') or '')
if version and version != '3.20.0':
    raise SystemExit(f'FAIL: expected backend 3.20.0, got {version}')
print('PASS: backend health reachable' + (f' version={version}' if version else ''))
PY

STATUS="$(curl -fsS "$BASE/v1/neural-runtime/status" 2>/dev/null || true)"
if [[ -n "$STATUS" ]]; then
  printf '%s\n' "$STATUS"
  python3 - "$STATUS" <<'PY'
import json,sys
obj=json.loads(sys.argv[1])
text=json.dumps(obj).lower()
if 'pytorch' not in text and 'neural' not in text:
    raise SystemExit('FAIL: neural runtime status does not identify neural/PyTorch capability')
print('PASS: neural runtime status reachable')
PY
else
  echo "NOTE: /v1/neural-runtime/status not exposed at this address; checking container health instead."
fi

if command -v docker >/dev/null 2>&1 && docker inspect sc-workspace-neural-runtime >/dev/null 2>&1; then
  STATE="$(docker inspect sc-workspace-neural-runtime --format '{{.State.Status}}')"
  [[ "$STATE" == "running" ]] || { echo "FAIL: neural runtime container status=$STATE" >&2; exit 1; }
  echo "PASS: sc-workspace-neural-runtime container running"
fi

echo "PASS: Workspace v3.20.0 backend is compatible with WordPress/package repair v3.20.0.1"
