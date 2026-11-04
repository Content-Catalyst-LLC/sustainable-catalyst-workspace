#!/usr/bin/env bash
# Run only as catalystadmin ON Contabo, after PB05_STAGE_FROM_MAC.sh.
# Creates an isolated, persistent test stack. Does not change existing containers.
set -euo pipefail
umask 077
STAGE="$HOME/rd014-pb05-browser-stage"
cd "$STAGE"
APP=sc-pb05-browser-app
DB=sc-pb05-browser-db
NET=sc-pb05-browser-net
DBVOL=sc-pb05-browser-pgdata
OBJVOL=sc-pb05-browser-objects
SRC="$STAGE/rd014_publication_records.py"
ORIG="$STAGE/source/wxr_private_projects.original.py"
LOG_DIR="$STAGE/logs"
mkdir -p "$LOG_DIR" "$STAGE/source" "$STAGE/tls" "$STAGE/overlays" "$STAGE/secrets"

for name in "$APP" "$DB"; do
  if docker container inspect "$name" >/dev/null 2>&1; then
    echo 'PB05_EXISTING_STAGE=YES; do not overwrite a previous test stack' >&2
    exit 3
  fi
done
if [[ -f "$STAGE/secrets/stage.env" ]]; then
  echo 'PB05_EXISTING_SECRETS=YES; do not overwrite prior acceptance data' >&2
  exit 3
fi
for vol in "$DBVOL" "$OBJVOL"; do
  if docker volume inspect "$vol" >/dev/null 2>&1; then
    echo 'PB05_EXISTING_TEST_VOLUME=YES; manual review required' >&2
    exit 3
  fi
done
if docker network inspect "$NET" >/dev/null 2>&1; then
  echo 'PB05_EXISTING_NETWORK=YES; manual review required' >&2
  exit 3
fi
if ! docker image inspect postgres:16-alpine >/dev/null 2>&1; then
  echo 'PB05_POSTGRES_IMAGE_NOT_CACHED=YES' >&2
  echo 'Run docker pull postgres:16-alpine separately, then rerun' >&2
  exit 4
fi
for tool in docker openssl python3 sha256sum curl; do
  command -v "$tool" >/dev/null || { echo "PB05_MISSING_TOOL=$tool" >&2; exit 4; }
done
if ! [[ -f "$SRC" ]] || \
   [[ "$(sha256sum "$SRC" | cut -d' ' -f1)" != '480fa0e797101a1f9662eb5d89de7391ff417bd17936e2e405bee1cac32b4f9c' ]]; then
  echo 'PB05_TESTED_PB04_SOURCE_MISSING_OR_DRIFTED=YES' >&2
  exit 4
fi
if ! docker inspect sc-rd013-staging-app >/dev/null 2>&1; then
  echo 'PB05_EXISTING_STAGING_IMAGE_NOT_FOUND=YES' >&2
  exit 4
fi
IMAGE="$(docker inspect --format '{{.Image}}' sc-rd013-staging-app)"
[[ "$IMAGE" == sha256:* ]] || { echo 'PB05_IMAGE_ID_INVALID=YES' >&2; exit 4; }
# Pull only the already-installed private-project source; never edit running app.
docker cp sc-rd013-staging-app:/app/app/wxr_private_projects.py "$ORIG"
mkdir -p "$STAGE/overlays"
python3 scripts/prepare_overlays.py "$ORIG" "$SRC" "$STAGE/overlays"

# Short-lived local TLS cert; browser access requires an SSH tunnel to localhost.
openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 7 \
  -keyout "$STAGE/tls/localhost.key" -out "$STAGE/tls/localhost.crt" \
  -subj '/CN=localhost' -addext 'subjectAltName=DNS:localhost,IP:127.0.0.1' \
  >/dev/null 2>&1
chmod 600 "$STAGE/tls/localhost.key"

DBPASS="$(openssl rand -hex 24)"
SESSION_SECRET="$(openssl rand -hex 32)"
LOGIN_CODE="$(openssl rand -hex 32)"
SECOND_LOGIN_CODE="$(openssl rand -hex 32)"
OWNER="pb05-synthetic-owner-$(openssl rand -hex 12)"
OTHER_OWNER="pb05-synthetic-owner-$(openssl rand -hex 12)"
printf '%s\n' "$LOGIN_CODE" > "$STAGE/secrets/login-code"
printf '%s\n' "$SECOND_LOGIN_CODE" > "$STAGE/secrets/other-login-code"
cat > "$STAGE/secrets/stage.env" <<EOF
PB05_STAGE_ENABLED=ISOLATED_TEST_ONLY
PB05_STAGE_ORIGIN=https://localhost:18443
PB05_STAGE_TEST_OWNER=$OWNER
PB05_STAGE_TEST_OTHER_OWNER=$OTHER_OWNER
PB05_STAGE_LOGIN_CODE=$LOGIN_CODE
PB05_STAGE_SECOND_LOGIN_CODE=$SECOND_LOGIN_CODE
SC_WORKSPACE_ENVIRONMENT=pb05-isolated
SC_WORKSPACE_DATABASE_URL=postgresql+psycopg://pb05test:$DBPASS@pb05-db:5432/pb05test
SC_WORKSPACE_SESSION_SIGNING_SECRET=$SESSION_SECRET
SC_WORKSPACE_SESSION_ISSUER=pb05-isolated
SC_WORKSPACE_SESSION_AUDIENCE=pb05-localhost-test
SC_WORKSPACE_SESSION_COOKIE_NAME=pb05_stage_session
SC_WORKSPACE_OBJECT_STORAGE_ROOT=/data/objects
SC_WORKSPACE_AUTO_CREATE_SCHEMA=false
PYTHONDONTWRITEBYTECODE=1
PYTHONWARNINGS=ignore::UserWarning
EOF
chmod 600 "$STAGE/secrets/stage.env" "$STAGE/secrets/login-code" "$STAGE/secrets/other-login-code"
cat > "$STAGE/secrets/db.env" <<EOF
POSTGRES_USER=pb05test
POSTGRES_PASSWORD=$DBPASS
POSTGRES_DB=pb05test
EOF
chmod 600 "$STAGE/secrets/db.env"

created=0
cleanup_on_failure() {
  if [[ "$created" != 1 ]]; then
    docker rm -f "$APP" "$DB" >/dev/null 2>&1 || true
    docker network rm "$NET" >/dev/null 2>&1 || true
    # Stage startup failure: remove only newly created, uniquely named test volumes.
    docker volume rm "$OBJVOL" "$DBVOL" >/dev/null 2>&1 || true
    echo 'PB05_STAGE_STARTUP=FAIL_TEST_RESOURCES_CLEANED' >&2
  fi
}
trap cleanup_on_failure EXIT

docker network create --internal --label sc.purpose=pb05-isolated-test "$NET" >/dev/null
docker volume create --label sc.purpose=pb05-isolated-test "$DBVOL" >/dev/null
docker volume create --label sc.purpose=pb05-isolated-test "$OBJVOL" >/dev/null
# TLS key and source overlays remain mode 0600; run only the test app as their host owner.
PB05_APP_UID="$(id -u)"
PB05_APP_GID="$(id -g)"
# Prepare the PB05-only object volume for the same UID/GID, never a production mount.
docker run --rm --network none --user 0 --entrypoint /bin/chown \
  --mount "type=volume,src=$OBJVOL,dst=/data/objects" \
  postgres:16-alpine "${PB05_APP_UID}:${PB05_APP_GID}" /data/objects
[[ -r "$STAGE/tls/localhost.key" ]] || { echo 'PB05_TLS_KEY_OWNER_READABLE=FAIL' >&2; exit 5; }
[[ "$(stat -c '%a' "$STAGE/tls/localhost.key")" == '600' ]] || { echo 'PB05_TLS_KEY_MODE=FAIL' >&2; exit 5; }
echo 'PB05_TLS_PRIVATE_KEY_MODE_0600=PASS'
echo 'PB05_APP_UID_MATCHES_TLS_OWNER=PASS'
docker run -d --name "$DB" --label sc.purpose=pb05-isolated-test --network "$NET" --network-alias pb05-db \
  --env-file "$STAGE/secrets/db.env" \
  --mount "type=volume,src=$DBVOL,dst=/var/lib/postgresql/data" \
  postgres:16-alpine >/dev/null
ready=0
for _ in $(seq 1 40); do
  if docker exec "$DB" pg_isready -U pb05test -d pb05test >/dev/null 2>&1; then ready=1; break; fi
  sleep 1
done
[[ "$ready" == 1 ]] || { echo 'PB05_DB_READY=FAIL' >&2; exit 5; }
echo PB05_DB_READY=PASS

# Initialize only the synthetic, isolated PostgreSQL database before web startup.
docker run --rm --network "$NET" --read-only --cap-drop ALL \
  --security-opt no-new-privileges --tmpfs /tmp:rw,nosuid,size=64m,mode=1777 \
  --env-file "$STAGE/secrets/stage.env" --entrypoint python "$IMAGE" \
  -c 'from app.db import initialize_schema; initialize_schema(); print("PB05_SCHEMA_INIT=PASS")'

# IMPORTANT: only publish on loopback. No production volumes, source, cookie or DB.
docker run -d --name "$APP" --label sc.purpose=pb05-isolated-test --network "$NET" \
  -p 127.0.0.1:18443:8443 \
  --user "${PB05_APP_UID}:${PB05_APP_GID}" \
  --read-only --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 128 --memory 1024m \
  --tmpfs /tmp:rw,nosuid,size=96m,mode=1777 \
  --env-file "$STAGE/secrets/stage.env" \
  --mount "type=volume,src=$OBJVOL,dst=/data/objects" \
  --mount "type=bind,src=$STAGE/overlays/wxr_private_projects.py,dst=/app/app/wxr_private_projects.py,readonly" \
  --mount "type=bind,src=$STAGE/overlays/rd014_publication_records.py,dst=/app/app/rd014_publication_records.py,readonly" \
  --mount "type=bind,src=$STAGE/source/pb05_browser_stage.py,dst=/app/app/pb05_browser_stage.py,readonly" \
  --mount "type=bind,src=$STAGE/tls,dst=/run/pb05,readonly" \
  --entrypoint python "$IMAGE" \
  -m uvicorn app.pb05_browser_stage:app --host 0.0.0.0 --port 8443 \
     --ssl-certfile /run/pb05/localhost.crt --ssl-keyfile /run/pb05/localhost.key \
  >/dev/null

for _ in $(seq 1 25); do
  code="$(curl -sk --connect-timeout 2 --max-time 3 -o /dev/null -w '%{http_code}' \
    -H 'Host: localhost:18443' https://127.0.0.1:18443/__pb05__/status || true)"
  if [[ "$code" == '200' ]]; then created=1; break; fi
  sleep 1
done
if [[ "$created" != 1 ]]; then
  echo 'PB05_STAGE_HTTPS_READY=FAIL' >&2
  docker logs --tail 25 "$APP" >&2 || true
  exit 6
fi
printf '%s\n' "$IMAGE" > "$STAGE/secrets/source-image-id"
cat > "$STAGE/secrets/stage-names" <<EOF
APP=$APP
DB=$DB
NETWORK=$NET
DB_VOLUME=$DBVOL
OBJECT_VOLUME=$OBJVOL
EOF
chmod 600 "$STAGE/secrets/stage-names"
echo 'PB05_STAGE_HTTPS_READY=PASS'
echo 'PB05_PRIVATE_PROJECT_ROUTER=MOUNTED_IN_ISOLATED_APP_ONLY'
echo 'PB05_PUBLICATION_ROUTER=MOUNTED_IN_ISOLATED_APP_ONLY'
echo 'PB05_TEST_OWNER=ISOLATED_SYNTHETIC_ONLY'
echo 'PB05_BROWSER_URL=https://localhost:18443/__pb05__/login'
echo 'PB05_PRODUCTION_CHANGES=NONE'
echo 'PB05_STAGE_RUNNING=PASS'
echo 'PB05_LOGIN_CODE=NOT_PRINTED'
echo "PB05_CERT_SHA256=$(sha256sum "$STAGE/tls/localhost.crt" | awk '{print $1}')"
echo 'Use SSH tunnel from Mac; retrieve test-only login code through your own SSH terminal, never paste it into chat.'
