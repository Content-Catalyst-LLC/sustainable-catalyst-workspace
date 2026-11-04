#!/usr/bin/env bash
# PB04: copy the candidate module to a separate Contabo staging directory and
# load it in a disposable, network-disabled, read-only container.
# Does not patch production/staging application files or start an HTTP service.
set -euo pipefail

LOCAL_ROOT="$HOME/Downloads/RD-01.4-PB04-Wexford-Two-Publication-Integration"
PACKAGE="$HOME/Downloads/RD-01.4-PB04-Wexford-Two-Publication-Integration-2026-11-03.zip"
SOURCE="$LOCAL_ROOT/backend/app/rd014_publication_records.py"
TARGET="catalystadmin@94.72.113.77"

if [[ ! -f "$SOURCE" ]]; then
  [[ -f "$PACKAGE" ]] || { echo 'PB04_PACKAGE_NOT_FOUND=YES' >&2; exit 2; }
  unzip -oq "$PACKAGE" -d "$HOME/Downloads"
fi
[[ -f "$SOURCE" ]] || { echo 'PB04_SOURCE_NOT_FOUND=YES' >&2; exit 2; }

EXPECTED="480fa0e797101a1f9662eb5d89de7391ff417bd17936e2e405bee1cac32b4f9c"
ACTUAL="$(shasum -a 256 "$SOURCE" | awk '{print $1}')"
[[ "$ACTUAL" == "$EXPECTED" ]] || {
  echo 'PB04_SOURCE_SHA256=FAIL; candidate differs from certified package' >&2
  exit 3
}
echo "PB04_LOCAL_SOURCE_SHA256=$ACTUAL"

ssh -T "$TARGET" 'mkdir -p "$HOME/rd014-pb04-contabo-candidate"'
scp -q "$SOURCE" "$TARGET:~/rd014-pb04-contabo-candidate/rd014_publication_records.py"

ssh -T "$TARGET" 'bash -se' <<'SERVER' | tee "$HOME/Downloads/PB04_CONTABO_ISOLATED_STAGE_RESULTS.txt"
set -euo pipefail
SOURCE="$HOME/rd014-pb04-contabo-candidate/rd014_publication_records.py"
EXPECTED="480fa0e797101a1f9662eb5d89de7391ff417bd17936e2e405bee1cac32b4f9c"
ACTUAL="$(sha256sum "$SOURCE" | awk '{print $1}')"
[[ "$ACTUAL" == "$EXPECTED" ]] || { echo 'PB04_REMOTE_SOURCE_SHA256=FAIL'; exit 3; }
echo PB04_REMOTE_SOURCE_SHA256=PASS

# Use the tested staging image, NOT the live image or any running container.
IMAGE="$(docker inspect --format '{{.Image}}' sc-rd013-staging-app)"
[[ "$IMAGE" == sha256:* ]] || { echo 'PB04_STAGING_IMAGE=UNAVAILABLE'; exit 4; }
echo "PB04_STAGING_IMAGE=$IMAGE"

# No production network, credentials, database, object-store volume or HTTP port.
docker run --rm -i \
  --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 64 --memory 768m --tmpfs /tmp:rw,nosuid,size=64m \
  -e PYTHONDONTWRITEBYTECODE=1 \
  --mount "type=bind,src=$SOURCE,dst=/app/app/rd014_publication_records.py,readonly" \
  --entrypoint python "$IMAGE" - <<'PY'
import importlib
from fastapi.routing import APIRoute

pb = importlib.import_module("app.rd014_publication_records")
candidate = [(m, r.path) for r in pb.router.routes if isinstance(r, APIRoute)
             for m in r.methods if m not in {"HEAD", "OPTIONS"}]
print("PB04_ISOLATED_MODULE_IMPORT=PASS")
print("PB04_CANDIDATE_ROUTE_COUNT=" + str(len(candidate)))
for method, path in sorted(candidate):
    print("PB04_CANDIDATE_ROUTE=" + method + " " + path)
if len(candidate) != len(set(candidate)):
    raise SystemExit("PB04_DUPLICATE_CANDIDATE_ROUTE=FAIL")

# Import is safe-guarded by no-network/read-only runtime. Startup events do not run.
try:
    live_module = importlib.import_module("app.main")
    app = live_module.app
except Exception as exc:
    print("PB04_EXISTING_APP_IMPORT=UNAVAILABLE_" + type(exc).__name__)
    raise SystemExit(5)

existing = [(m, r.path) for r in app.routes if isinstance(r, APIRoute)
            for m in r.methods if m not in {"HEAD", "OPTIONS"}]
old = set(existing)
overlap = sorted(old.intersection(candidate))
print("PB04_EXISTING_APP_IMPORT=PASS")
print("PB04_EXISTING_ROUTE_COUNT=" + str(len(existing)))
print("PB04_EXISTING_PROJECT_ROUTE_COUNT=" + str(sum(
    1 for _, p in existing if p.startswith("/v1/private-research/persistent-projects"))))
print("PB04_ROUTE_COLLISIONS=" + str(len(overlap)))
for method, path in overlap:
    print("PB04_COLLISION=" + method + " " + path)
if overlap:
    raise SystemExit(6)
print("PB04_ISOLATED_CANDIDATE_COMPATIBILITY=PASS")
PY

echo PB04_OWNER_SESSION=NOT_USED
echo PB04_DATABASE_WRITES=NONE
echo PB04_PRODUCTION_CHANGES=NONE
echo PB04_CONTABO_ISOLATED_STAGE=COMPLETE
SERVER
