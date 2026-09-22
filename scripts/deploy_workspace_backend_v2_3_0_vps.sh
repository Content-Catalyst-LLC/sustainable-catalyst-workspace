#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v2.3.0.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v2.2.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v2.3.0"

if [[ ! -f "$ZIP_PATH" ]]; then
  echo "ERROR: backend zip not found: $ZIP_PATH" >&2
  exit 1
fi
if [[ ! -f "$OLD/.env" ]]; then
  echo "ERROR: v2.2.0 backend .env not found at $OLD/.env" >&2
  exit 1
fi

echo "=== WORKSPACE BACKEND v2.3.0 UPGRADE ==="
rm -rf "$NEW"
unzip -q "$ZIP_PATH" -d "$BASE"
cp "$OLD/.env" "$NEW/.env"
chmod 600 "$NEW/.env"

cd "$NEW"
cp docker-compose.example.yml docker-compose.yml

# Add optional route variables without overwriting existing secrets/config.
for name in CORE LAB WORKBENCH DECISION_STUDIO LIBRARY SITE_INTELLIGENCE; do
  grep -q "^SC_WORKSPACE_ROUTE_${name}_URL=" .env || echo "SC_WORKSPACE_ROUTE_${name}_URL=" >> .env
  grep -q "^SC_WORKSPACE_ROUTE_${name}_TOKEN=" .env || echo "SC_WORKSPACE_ROUTE_${name}_TOKEN=" >> .env
done

echo "=== STOP v2.2.0 API / ANY OLD WORKER ==="
docker rm -f sc-workspace-worker 2>/dev/null || true
docker rm -f sc-workspace-backend 2>/dev/null || true

echo "=== BUILD + START v2.3.0 API AND WORKER ==="
docker compose --env-file .env -f docker-compose.yml up -d --build

echo "=== WAIT FOR API HEALTH ==="
for i in $(seq 1 30); do
  code="$(curl -sS -o /tmp/sc-workspace-v230-health.json -w '%{http_code}' http://127.0.0.1:8094/health 2>/dev/null || true)"
  echo "attempt $i: HTTP ${code:-000}"
  if [[ "$code" == "200" ]]; then break; fi
  sleep 2
done
python3 -m json.tool /tmp/sc-workspace-v230-health.json

echo "=== READINESS ==="
curl -fsS http://127.0.0.1:8094/ready | python3 -m json.tool

set -a
. ./.env
set +a

AUTH=( -H "Authorization: Bearer ${SC_WORKSPACE_SERVICE_TOKEN}" -H "X-SC-User-ID: 1" )

echo "=== CAPABILITIES ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/capabilities | python3 -m json.tool

echo "=== WORKER HEARTBEAT ==="
for i in $(seq 1 20); do
  curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/worker/status > /tmp/sc-workspace-v230-worker.json
  if python3 - <<'PY'
import json
p='/tmp/sc-workspace-v230-worker.json'
d=json.load(open(p))
raise SystemExit(0 if any(x.get('version')=='2.3.0' and x.get('status') in ('idle','running') for x in d.get('items',[])) else 1)
PY
  then break; fi
  echo "waiting for worker heartbeat: $i"
  sleep 2
done
python3 -m json.tool /tmp/sc-workspace-v230-worker.json

echo "=== ORCHESTRATION ROUTES ==="
curl -fsS "${AUTH[@]}" http://127.0.0.1:8094/v1/orchestration/routes | python3 -m json.tool

echo "=== JOB QUEUE SMOKE: workspace.echo ==="
IDEMPOTENCY="deploy-v230-$(date +%s)"
cat > /tmp/sc-workspace-v230-job.json <<JSON
{
  "schema":"sc-workspace-job-request/1.0",
  "jobType":"workspace-task",
  "targetProduct":"workspace",
  "operation":"workspace.echo",
  "priority":9,
  "maxAttempts":1,
  "idempotencyKey":"${IDEMPOTENCY}",
  "payload":{"deploymentSmoke":true,"version":"2.3.0"}
}
JSON
curl -fsS "${AUTH[@]}" -H 'Content-Type: application/json' \
  --data-binary @/tmp/sc-workspace-v230-job.json \
  http://127.0.0.1:8094/v1/jobs > /tmp/sc-workspace-v230-job-created.json
python3 -m json.tool /tmp/sc-workspace-v230-job-created.json
JOB_ID="$(python3 - <<'PY'
import json
print(json.load(open('/tmp/sc-workspace-v230-job-created.json'))['item']['jobId'])
PY
)"

for i in $(seq 1 30); do
  curl -fsS "${AUTH[@]}" "http://127.0.0.1:8094/v1/jobs/${JOB_ID}" > /tmp/sc-workspace-v230-job-status.json
  STATUS="$(python3 - <<'PY'
import json
print(json.load(open('/tmp/sc-workspace-v230-job-status.json'))['item']['status'])
PY
)"
  echo "job ${JOB_ID}: ${STATUS}"
  [[ "$STATUS" == "succeeded" ]] && break
  [[ "$STATUS" == "failed" || "$STATUS" == "blocked" || "$STATUS" == "cancelled" ]] && break
  sleep 1
done
python3 -m json.tool /tmp/sc-workspace-v230-job-status.json
if [[ "${STATUS}" != "succeeded" ]]; then
  echo "ERROR: v2.3.0 smoke job did not succeed" >&2
  exit 1
fi

echo "=== CONTAINERS ==="
docker ps --filter name=sc-workspace --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo "PASS: Workspace backend v2.3.0 API + worker + durable job queue are running."
