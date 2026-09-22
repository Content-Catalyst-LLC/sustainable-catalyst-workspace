# Deploy Workspace Backend v3.1.0

Workspace v3.1.0 integrates the backend-native Workspace with Platform Core v3.0's unified research runtime. Deploy the backend before installing the WordPress plugin.

## VPS

```bash
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes catalystadmin@94.72.113.77
cd /opt/sustainable-catalyst
```

Copy `sustainable-catalyst-workspace-backend-v3.1.0.zip` to `/tmp/`, then run:

```bash
chmod +x /tmp/deploy_workspace_backend_v3_1_0_vps.sh
bash /tmp/deploy_workspace_backend_v3_1_0_vps.sh \
  /tmp/sustainable-catalyst-workspace-backend-v3.1.0.zip
```

The deploy script applies migration 032, verifies Platform Core v3's runtime contract, discovers the Core write key from the running `sc-core` container without exposing it to the browser, rebuilds Workspace, and verifies the Workspace→Core readiness route.

## Independent verification

```bash
curl -fsS http://127.0.0.1:8094/health | python3 -m json.tool
```

With the Workspace service token from the server `.env`:

```bash
TOKEN="$(awk -F= '$1=="SC_WORKSPACE_SERVICE_TOKEN"{sub(/^[^=]*=/,"");print;exit}' /opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.1.0/.env)"
curl -fsS -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8094/v1/platform-core-runtime/readiness | python3 -m json.tool
```

Expected: Workspace `version` 3.1.0, `platformCoreV3UnifiedResearchRuntimeIntegration: true`, and readiness `compatible: true` for contract `sc.research.unified-research-scientific-investigation-runtime.v1`.
