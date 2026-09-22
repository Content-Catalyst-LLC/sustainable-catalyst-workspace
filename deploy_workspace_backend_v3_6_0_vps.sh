#!/usr/bin/env bash
set -euo pipefail
OVERLAY_ZIP="${1:-/tmp/sustainable-catalyst-workspace-backend-v3.6.0-overlay.zip}"
BASE="/opt/sustainable-catalyst"
OLD="$BASE/sustainable-catalyst-workspace-backend-v3.5.0"
NEW="$BASE/sustainable-catalyst-workspace-backend-v3.6.0"
[[ -f "$OVERLAY_ZIP" ]] || { echo "ERROR: backend overlay not found: $OVERLAY_ZIP" >&2; exit 1; }
[[ -d "$OLD" ]] || { echo "ERROR: verified Workspace v3.5 backend directory not found: $OLD" >&2; exit 1; }
[[ -f "$OLD/migrations/036_catalyst_analytics_r_runtime_adapter.sql" ]] || { echo "ERROR: deployed Analytics R migration 036 missing; refusing v3.6 deployment." >&2; exit 1; }
[[ -f "$OLD/app/analytics_r_provider.py" ]] || { echo "ERROR: deployed Analytics R provider module missing; refusing v3.6 deployment." >&2; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$OVERLAY_ZIP" -d "$TMP"
[[ -f "$TMP/apply_workspace_v3600.py" ]] || { echo "ERROR: malformed overlay" >&2; exit 1; }

rm -rf "$NEW"
cp -a "$OLD" "$NEW"
# The patcher uses repository-relative backend/ paths. Wrap the deployed backend
# in a temporary repository-shaped symlink so only the copied v3.6 tree changes.
WRAP="$TMP/repo-shape"
mkdir -p "$WRAP"
ln -s "$NEW" "$WRAP/backend"
python3 "$TMP/apply_workspace_v3600.py" "$WRAP" --payload "$TMP/payload" --backend-only
python3 -m compileall -q "$NEW/app"

cd "$NEW"
[[ -f docker-compose.yml ]] || { [[ -f docker-compose.example.yml ]] && cp docker-compose.example.yml docker-compose.yml; }
[[ -f docker-compose.yml ]] || { echo "ERROR: docker-compose.yml not found" >&2; exit 1; }
[[ -f .env ]] || { echo "ERROR: v3.5 .env was not preserved into v3.6 deployment tree" >&2; exit 1; }

echo "=== APPLY MIGRATION 037 ==="
PG_ADMIN_USER="$(docker inspect sc-postgres --format '{{range .Config.Env}}{{println .}}{{end}}' | awk -F= '$1=="POSTGRES_USER"{print $2}' | tail -1)"
PG_ADMIN_USER="${PG_ADMIN_USER:-postgres}"
docker exec -i sc-postgres psql -v ON_ERROR_STOP=1 -U "$PG_ADMIN_USER" -d sustainable_catalyst < migrations/037_platform_core_visual_analysis_research_object_workspace.sql

echo "=== REBUILD MERGED v3.6 BACKEND ==="
docker compose --env-file .env -f docker-compose.yml up -d --build

for i in $(seq 1 25); do
  code="$(curl -sS -o /tmp/scw360-health.json -w '%{http_code}' http://127.0.0.1:8094/health || true)"
  echo "health attempt $i: HTTP $code"
  [[ "$code" == "200" ]] && break
  sleep 2
done

echo "=== WORKSPACE v3.6 HEALTH ==="
python3 - <<'PY'
import json
p='/tmp/scw360-health.json'
d=json.load(open(p))
assert d['ok'] is True, d
assert d['version']=='3.6.0', d
# v3.5 Analytics R must survive the upgrade.
assert d.get('catalystAnalyticsRRuntimeAdapter') is True, d
assert d.get('catalystAnalyticsRProviderInstalled') is True, d
assert d.get('catalystAnalyticsRProviderVersion')=='2.1.0', d
assert d.get('catalystAnalyticsRCoreContract')=='sc.core.analytical-runtime-provider.v1', d
assert d.get('analyticalProviderReceipts') is True, d
# v3.6 visual layer.
assert d.get('platformCoreVisualAnalysisResearchObjectWorkspace') is True, d
assert d.get('visualResearchSceneGraph') is True, d
assert d.get('visualResearchExplicitCoreBinding') is True, d
assert d.get('visualResearchImmutableSnapshots') is True, d
assert d.get('releaseMigrationLineage')=='037_platform_core_visual_analysis_research_object_workspace.sql', d
print('WORKSPACE_V360_HEALTH=PASS')
PY

echo "=== OPENAPI VISUAL ROUTES ==="
docker exec -i sc-workspace-backend python3 - <<'PY'
from app.main import app
from app.client_contracts import TYPED_ENDPOINTS, profile
x=profile(app.openapi())
assert x['workspaceVersion']=='3.6.0', x
assert not x['missingOpenApiOperations'], x
keys=['visualResearchWorkspace','visualResearchProject','visualResearchVisualization','visualResearchVisualizationBind','visualResearchSnapshotCreate','visualResearchSnapshots']
for key in keys: assert key in TYPED_ENDPOINTS, key
print('WORKSPACE_V360_OPENAPI=PASS typed_endpoints=%d' % len(TYPED_ENDPOINTS))
PY

echo "=== ANALYTICS R PROVIDER PRESERVATION ==="
docker exec sc-workspace-r-runtime Rscript --vanilla -e '
  library(catalystanalyticsr)
  p <- catalyst_core_provider_manifest()
  stopifnot(
    as.character(packageVersion("catalystanalyticsr")) == "2.1.0",
    p$provider_key == "catalystanalyticsr",
    p$core_contract == "sc.core.analytical-runtime-provider.v1",
    p$runtime == "r",
    p$execution_host == "workspace",
    identical(p$boundary$core_executes_provider, FALSE)
  )
  cat("CATALYST_ANALYTICS_R_PROVIDER=PASS\n")
'

echo "=== RUNTIME HARDENING ==="
docker inspect sc-workspace-r-runtime --format 'ReadonlyRootfs={{.HostConfig.ReadonlyRootfs}} User={{.Config.User}}'

echo "=== MIGRATION 037 REGISTRY ==="
docker exec -i sc-postgres psql -v ON_ERROR_STOP=1 -U "$PG_ADMIN_USER" -d sustainable_catalyst -Atc "SELECT to_regclass('public.workspace_visual_research_workspace_snapshots');" | grep -qx 'workspace_visual_research_workspace_snapshots'
echo "WORKSPACE_V360_MIGRATION_037=PASS"

echo "PASS: Workspace v3.6.0 backend deployed; Analytics R v3.5 preserved; visual research layer active"
