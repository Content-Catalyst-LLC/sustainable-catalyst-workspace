#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.2.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v2.1.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.2.0"

if [[ ! -f "$ZIP_PATH" ]]; then
  echo "ERROR: backend zip not found: $ZIP_PATH" >&2
  exit 1
fi
if [[ ! -f "$OLD/.env" ]]; then
  echo "ERROR: v2.1.0 backend .env not found at $OLD/.env" >&2
  exit 1
fi

echo "=== WORKSPACE BACKEND v2.2.0 UPGRADE ==="
rm -rf "$NEW"
unzip -q "$ZIP_PATH" -d "$BASE"
cp "$OLD/.env" "$NEW/.env"
chmod 600 "$NEW/.env"

cd "$NEW"
cp docker-compose.example.yml docker-compose.yml

echo "=== STOP OLD WORKSPACE CONTAINER ==="
docker rm -f sc-workspace-backend 2>/dev/null || true

echo "=== BUILD + START v2.2.0 ==="
docker compose --env-file .env -f docker-compose.yml up -d --build

echo "=== WAIT FOR HEALTH ==="
for i in $(seq 1 30); do
  code="$(curl -sS -o /tmp/sc-workspace-v220-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "attempt $i: HTTP ${code:-000}"
  if [[ "$code" == "200" ]]; then break; fi
  sleep 2
done

python3 -m json.tool /tmp/sc-workspace-v220-health.json

echo "=== READINESS ==="
curl -fsS http://127.0.0.1:8094/ready | python3 -m json.tool

set -a
. ./.env
set +a

echo "=== CAPABILITIES ==="
curl -fsS \
  -H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" \
  -H "X-SC-User-ID: 1" \
  http://127.0.0.1:8094/v1/capabilities | python3 -m json.tool

echo "=== STORAGE INTEGRITY ==="
curl -fsS \
  -H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" \
  -H "X-SC-User-ID: 1" \
  http://127.0.0.1:8094/v1/storage/integrity | python3 -m json.tool

echo "=== CONTAINER ==="
docker ps --filter name=sc-workspace-backend --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo "PASS: Workspace backend v2.2.0 is running."
