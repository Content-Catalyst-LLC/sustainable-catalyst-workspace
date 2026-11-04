#!/usr/bin/env bash
# PB05: disposable network probe, NOT a Workspace deployment.
# Execute on Contabo as catalystadmin. Creates only one temporary internal
# Docker bridge and a tiny HTTP server container without DB/storage/secrets.
set -euo pipefail
umask 077
for tool in docker curl; do command -v "$tool" >/dev/null || { echo "PB05_DIAG_MISSING_TOOL=$tool"; exit 2; }; done
IMAGE="$(docker inspect --format '{{.Image}}' sc-rd013-staging-app)"
[[ "$IMAGE" == sha256:* ]] || { echo 'PB05_DIAG_STAGING_IMAGE_MISSING=YES'; exit 2; }
NET="sc-pb05-diag-net-$$"
CTR="sc-pb05-diag-http-$$"
cleanup() {
  docker rm -f "$CTR" >/dev/null 2>&1 || true
  docker network rm "$NET" >/dev/null 2>&1 || true
}
trap cleanup EXIT
for n in "$NET" "$CTR"; do
  if docker network inspect "$n" >/dev/null 2>&1 || docker container inspect "$n" >/dev/null 2>&1; then
    echo 'PB05_DIAG_NAME_COLLISION=YES'; exit 3
  fi
done
if [[ -n "${HTTPS_PROXY:-}${HTTP_PROXY:-}${ALL_PROXY:-}${https_proxy:-}${http_proxy:-}${all_proxy:-}" ]]; then
  echo 'PB05_HOST_PROXY_ENV_CONFIGURED=YES'
else
  echo 'PB05_HOST_PROXY_ENV_CONFIGURED=NO'
fi
docker network create --internal --label sc.purpose=pb05-disposable-diagnostic "$NET" >/dev/null
docker run -d --name "$CTR" \
  --label sc.purpose=pb05-disposable-diagnostic \
  --network "$NET" -p '127.0.0.1::8443' \
  --read-only --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 64 --memory 128m \
  --tmpfs /tmp:rw,nosuid,size=8m \
  --entrypoint python "$IMAGE" \
  -m http.server 8443 --bind 0.0.0.0 --directory /tmp >/dev/null
PORT_MAPPING="$(docker port "$CTR" 8443/tcp | head -1)"
case "$PORT_MAPPING" in 127.0.0.1:*) PORT="${PORT_MAPPING##*:}" ;; *) echo 'PB05_DIAG_UNSAFE_NON_LOOPBACK_MAPPING=YES'; exit 4;; esac
[[ "$PORT" =~ ^[0-9]+$ ]] || { echo 'PB05_DIAG_PORT_PARSE=FAIL'; exit 4; }
echo 'PB05_DIAG_LOOPBACK_BIND=PASS'
INSIDE=FAIL
for attempt in 1 2 3 4 5; do
  if docker exec "$CTR" python -c 'from urllib.request import urlopen; assert urlopen("http://127.0.0.1:8443/", timeout=2).status == 200' >/dev/null 2>&1; then INSIDE=PASS; break; fi
  sleep 1
done
echo "PB05_DIAG_IN_CONTAINER_HTTP=$INSIDE"
HOST=FAIL
for attempt in 1 2 3 4 5; do
  if curl --noproxy '*' --silent --show-error --fail --connect-timeout 3 --max-time 5 \
      -o /dev/null "http://127.0.0.1:${PORT}/" 2>/dev/null; then HOST=PASS; break; fi
  sleep 1
done
echo "PB05_DIAG_HOST_PUBLISHED_HTTP=$HOST"
if [[ "$INSIDE" == PASS && "$HOST" == FAIL ]]; then
  echo 'PB05_DIAG_CONCLUSION=INTERNAL_BRIDGE_PUBLISHING_OR_HOST_FIREWALL_PATH_FAILURE'
elif [[ "$INSIDE" == PASS && "$HOST" == PASS ]]; then
  echo 'PB05_DIAG_CONCLUSION=INTERNAL_BRIDGE_HOST_PATH_WORKS_CHECK_PB05_HTTPS_HEALTH_REQUEST'
else
  echo 'PB05_DIAG_CONCLUSION=DOCKER_TEST_SERVER_DID_NOT_RESPOND_INSIDE_CONTAINER'
fi
echo 'PB05_DIAG_EVIDENCE=TRANSIENT_PLAIN_HTTP_NETWORK_ONLY_NOT_WORKSPACE_TLS'
echo 'PB05_PRODUCTION_CHANGES=NONE'
echo 'PB05_DIAGNOSTIC=COMPLETE'
