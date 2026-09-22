#!/usr/bin/env bash
set -euo pipefail

ZIP_PATH="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.9.1.zip}"
BASE="/opt/sustainable-catalyst"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.9.1"

[[ -f "$ZIP_PATH" ]] || { echo "ERROR: backend ZIP not found: $ZIP_PATH" >&2; exit 1; }

echo "=== WORKSPACE v3.9.1 PREDECESSOR GATE ==="
ENV_SOURCE=""
for candidate in \
  "$BASE/sustainable-catalyst-workspace-backend-v3.9.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v3.8.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v3.7.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v3.6.0/.env" \
  "$BASE/sustainable-catalyst-workspace-backend-v3.5.0/.env"
do
  if [[ -f "$candidate" ]]; then ENV_SOURCE="$candidate"; break; fi
done
[[ -n "$ENV_SOURCE" ]] || { echo "ERROR: no prior Workspace backend .env found" >&2; exit 1; }
echo "Using environment from: $ENV_SOURCE"

docker ps --format '{{.Names}}' | grep -qx sc-postgres || { echo "ERROR: sc-postgres is not running" >&2; exit 1; }
PG_ADMIN_USER="$(docker inspect sc-postgres --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '$1=="POSTGRES_USER"{print $2; exit}')"
PG_ADMIN_USER="${PG_ADMIN_USER:-postgres}"

docker exec -i sc-postgres psql -v ON_ERROR_STOP=1 -U "$PG_ADMIN_USER" -d sc_workspace -Atc \
  "SELECT to_regclass('public.workspace_investigation_event_heads');" | grep -qx 'workspace_investigation_event_heads' \
  || { echo "ERROR: v3.9 migration 040 timeline tables are not present" >&2; exit 1; }
docker exec -i sc-postgres psql -v ON_ERROR_STOP=1 -U "$PG_ADMIN_USER" -d sc_workspace -Atc \
  "SELECT to_regclass('public.workspace_analytical_provider_receipts');" | grep -qx 'workspace_analytical_provider_receipts' \
  || { echo "ERROR: Analytics R receipt table from migration 036 is not present" >&2; exit 1; }
echo "WORKSPACE_V391_PREDECESSOR=PASS"

SNAP="$(mktemp)"
cp "$ENV_SOURCE" "$SNAP"
chmod 600 "$SNAP"
trap 'rm -f "$SNAP"' EXIT

rm -rf "$NEW"
unzip -q "$ZIP_PATH" -d "$BASE"
[[ -d "$NEW" ]] || { echo "ERROR: backend ZIP did not create $NEW" >&2; exit 1; }
cp "$SNAP" "$NEW/.env"
chmod 600 "$NEW/.env"
cd "$NEW"
cp docker-compose.example.yml docker-compose.yml

echo "=== NO DATABASE MIGRATION REQUIRED ==="
[[ -f migrations/040_timeline_event_reconstruction_investigative_sequence_workspace.sql ]] \
  || { echo "ERROR: migration 040 lineage file missing" >&2; exit 1; }
if find migrations -maxdepth 1 -type f -name '041_*.sql' | grep -q .; then
  echo "ERROR: v3.9.1 provider promotion unexpectedly contains migration 041" >&2
  exit 1
fi

echo "=== REBUILD v3.9.1 BACKEND + R PROVIDER ==="
docker compose --env-file .env -f docker-compose.yml build \
  sc-workspace-r-runtime sc-workspace-backend sc-workspace-worker
docker compose --env-file .env -f docker-compose.yml up -d --no-build \
  sc-workspace-r-runtime sc-workspace-backend sc-workspace-worker

for i in $(seq 1 35); do
  code="$(curl -sS -o /tmp/scw391-health.json -w '%{http_code}' http://127.0.0.1:8094/health || true)"
  echo "health attempt $i: HTTP $code"
  [[ "$code" == "200" ]] && break
  sleep 2
done

echo "=== WORKSPACE v3.9.1 HEALTH ==="
python3 - <<'PY'
import json
p='/tmp/scw391-health.json'
d=json.load(open(p))
assert d['ok'] is True, d
assert d['version']=='3.9.1', d
assert d.get('catalystAnalyticsRRuntimeAdapter') is True, d
assert d.get('catalystAnalyticsRProviderInstalled') is True, d
assert d.get('catalystAnalyticsRProviderVersion')=='2.2.0', d
assert d.get('catalystAnalyticsRCoreContract')=='sc.core.analytical-runtime-provider.v1', d
assert d.get('catalystAnalyticsRDiagnosticsContract')=='sc.analytics-r.statistical-diagnostics-validation.v1', d
assert d.get('catalystAnalyticsRStatisticalDiagnosticsValidation') is True, d
assert d.get('catalystAnalyticsRAdapterVersion')=='3.9.1', d
assert d.get('analyticalProviderReceipts') is True, d
assert d.get('timelineEventReconstructionWorkspace') is True, d
assert d.get('releaseMigrationLineage')=='040_timeline_event_reconstruction_investigative_sequence_workspace.sql', d
print('WORKSPACE_V391_HEALTH=PASS')
PY

echo "=== CATALYST ANALYTICS R v2.2.0 PACKAGE ==="
docker exec sc-workspace-r-runtime Rscript --vanilla -e '
  library(catalystanalyticsr)
  p <- catalyst_core_provider_manifest()
  stopifnot(
    as.character(packageVersion("catalystanalyticsr")) == "2.2.0",
    p$provider_key == "catalystanalyticsr",
    p$provider_version == "2.2.0",
    p$core_contract == "sc.core.analytical-runtime-provider.v1",
    p$diagnostics_contract == "sc.analytics-r.statistical-diagnostics-validation.v1",
    p$runtime == "r",
    p$execution_host == "workspace",
    identical(p$boundary$core_executes_provider, FALSE),
    identical(p$boundary$human_review_required, TRUE)
  )
  cat("CATALYST_ANALYTICS_R_V220_PROVIDER=PASS\n")
'

echo "=== R SERVICE METADATA ==="
docker exec -i sc-workspace-r-runtime python - <<'PY'
import json, urllib.request
with urllib.request.urlopen('http://127.0.0.1:8090/health', timeout=5) as r:
    d=json.load(r)
assert d['ok'] is True, d
assert d['catalystAnalyticsRProviderVersion']=='2.2.0', d
assert d['catalystAnalyticsRAdapterVersion']=='3.9.1', d
assert d['catalystAnalyticsRDiagnosticsContract']=='sc.analytics-r.statistical-diagnostics-validation.v1', d
assert d['catalystAnalyticsRStatisticalDiagnosticsValidation'] is True, d
print('CATALYST_ANALYTICS_R_V220_SERVICE=PASS')
PY

echo "=== TYPED CLIENT / OPENAPI REGRESSION ==="
docker exec -i sc-workspace-backend python3 - <<'PY'
from app.main import app
from app.client_contracts import profile
p=profile(app.openapi())
assert p['workspaceVersion']=='3.9.1', p
assert p['typedEndpointCount']==111, p
assert p['missingOpenApiOperations']==[], p
print('WORKSPACE_V391_OPENAPI=PASS typed_endpoints=%d' % p['typedEndpointCount'])
PY

echo "=== RUNTIME HARDENING ==="
HARDENING="$(docker inspect sc-workspace-r-runtime --format 'ReadonlyRootfs={{.HostConfig.ReadonlyRootfs}} User={{.Config.User}}')"
echo "$HARDENING"
[[ "$HARDENING" == 'ReadonlyRootfs=true User=10001' ]] || { echo "ERROR: R runtime hardening mismatch" >&2; exit 1; }

echo "=== MIGRATION LINEAGE PRESERVED ==="
docker exec -i sc-postgres psql -v ON_ERROR_STOP=1 -U "$PG_ADMIN_USER" -d sc_workspace -Atc \
  "SELECT to_regclass('public.workspace_investigation_timeline_snapshots');" | grep -qx 'workspace_investigation_timeline_snapshots'
echo "WORKSPACE_V391_MIGRATION_LINEAGE=PASS"

echo "PASS - Workspace v3.9.1 Catalyst Analytics R v2.2 Provider Promotion"
echo "PASS - WORKSPACE v3.9.1 BACKEND DEPLOYMENT COMPLETE"
