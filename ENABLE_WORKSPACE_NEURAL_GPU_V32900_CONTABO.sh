#!/usr/bin/env bash
set -euo pipefail
BASE="${1:-/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.29.0}"
cd "$BASE"
[[ -f .env && -f docker-compose.yml && -f docker-compose.neural-gpu.example.yml ]] || { echo "ERROR: v3.29.0 backend or GPU override missing" >&2; exit 1; }
command -v nvidia-smi >/dev/null 2>&1 || { echo "ERROR: nvidia-smi not available on this host" >&2; exit 1; }
nvidia-smi >/dev/null
if grep -q '^SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED=' .env; then sed -i 's/^SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED=.*/SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED=true/' .env; else echo 'SC_WORKSPACE_NEURAL_ACCELERATOR_ENABLED=true' >> .env; fi
if grep -q '^SC_WORKSPACE_NEURAL_ALLOWED_DEVICES=' .env; then sed -i 's/^SC_WORKSPACE_NEURAL_ALLOWED_DEVICES=.*/SC_WORKSPACE_NEURAL_ALLOWED_DEVICES=cpu,cuda:0/' .env; else echo 'SC_WORKSPACE_NEURAL_ALLOWED_DEVICES=cpu,cuda:0' >> .env; fi
docker compose --env-file .env -f docker-compose.yml -f docker-compose.neural-gpu.example.yml up -d --no-deps sc-workspace-neural-runtime
docker exec -i sc-workspace-neural-runtime python - <<'PYCODE'
import json,urllib.request
x=json.load(urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=10))
assert x['version']=='3.29.0' and x['acceleratorPolicyEnabled'] is True,x
cuda=[d for d in x.get('availableDevices',[]) if str(d).startswith('cuda:')]
assert cuda,x
print('NEURAL_V32900_GPU_ACTIVATION=PASS devices='+','.join(x['availableDevices']))
PYCODE
