from __future__ import annotations
from typing import Any
from .command_query import COMMANDS, QUERIES
from .utils import sha256_hex

CLIENT_CONTRACT_SCHEMA = "sc-workspace-typed-client-contract/1.0"
CLIENT_RUNTIME_SCHEMA = "sc-workspace-typed-client-runtime/1.0"
TYPED_ENDPOINTS: dict[str, dict[str, str]] = {
    "clientContracts": {"method": "GET", "path": "/v1/client-contracts"},
    "thinClientState": {"method": "GET", "path": "/v1/thin-client-state"},
    "thinClientBootstrap": {"method": "GET", "path": "/v1/thin-client-state/bootstrap"},
    "syncProfile": {"method": "GET", "path": "/v1/sync"},
    "syncBootstrap": {"method": "GET", "path": "/v1/sync/bootstrap"},
    "syncEnvelope": {"method": "POST", "path": "/v1/sync/envelopes"},
    "syncReconcile": {"method": "POST", "path": "/v1/sync/reconcile"},
    "syncReceipts": {"method": "GET", "path": "/v1/sync/receipts"},
    "domainAuthority": {"method": "GET", "path": "/v1/domain-authority"},
    "commandQuery": {"method": "GET", "path": "/v1/command-query"},
    "executeCommand": {"method": "POST", "path": "/v1/commands/execute"},
    "executeQuery": {"method": "POST", "path": "/v1/queries/execute"},
    "workspaceOverview": {"method": "GET", "path": "/v1/read-models/workspace-overview"},
    "notebookOrchestration": {"method": "GET", "path": "/v1/notebook-orchestration"},
    "notebookPlans": {"method": "POST", "path": "/v1/notebook-execution-plans"},
    "studyPackageProfile": {"method": "GET", "path": "/v1/scientific-study-packages/profile"},
    "studyPackages": {"method": "POST", "path": "/v1/scientific-study-packages"},
    "visualizationProfile": {"method": "GET", "path": "/v1/visualization-specs/profile"},
    "visualizationSpecs": {"method": "POST", "path": "/v1/visualization-specs"},
    "visualizationReceipts": {"method": "GET", "path": "/v1/visualization-spec-receipts"},
}
REQUEST_SCHEMAS = {
    "executeCommand": "sc-workspace-command-request/1.0",
    "executeQuery": "sc-workspace-query-request/1.0",
    "notebookPlans": "sc-workspace-notebook-execution-plan-request/1.0",
    "studyPackages": "sc-workspace-scientific-study-package-request/1.0",
    "visualizationSpecs": "sc-workspace-visualization-spec-request/1.0",
    "syncEnvelope": "sc-workspace-sync-envelope/1.0",
    "syncReconcile": "sc-workspace-sync-reconcile-request/1.0",
}

def _typed_openapi_projection(openapi: dict[str, Any]) -> dict[str, Any]:
    paths = openapi.get("paths") or {}
    projection: dict[str, Any] = {"openapi": openapi.get("openapi"), "version": (openapi.get("info") or {}).get("version"), "paths": {}}
    for key, endpoint in TYPED_ENDPOINTS.items():
        path = endpoint["path"]
        method = endpoint["method"].lower()
        operation = (paths.get(path) or {}).get(method)
        projection["paths"][key] = {
            "method": endpoint["method"], "path": path,
            "operationId": (operation or {}).get("operationId", ""),
            "requestBody": (operation or {}).get("requestBody"),
            "responses": (operation or {}).get("responses"),
        }
    return projection

def profile(openapi: dict[str, Any]) -> dict[str, Any]:
    projection = _typed_openapi_projection(openapi)
    missing = [key for key, item in projection["paths"].items() if not item.get("operationId")]
    return {
        "schema": CLIENT_CONTRACT_SCHEMA,
        "workspaceVersion": "2.31.0",
        "mode": "generated-typescript-local-first-thin-client",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "transport": "wordpress-server-proxy",
        "browserDirectBackendAccess": False,
        "serviceCredentialsBrowserVisible": False,
        "generatedFromOpenApi": True,
        "openApiProjectionSha256": sha256_hex(projection),
        "typedEndpointCount": len(TYPED_ENDPOINTS),
        "typedEndpoints": TYPED_ENDPOINTS,
        "requestSchemas": REQUEST_SCHEMAS,
        "commandCount": len(COMMANDS), "commands": list(COMMANDS),
        "queryCount": len(QUERIES), "queries": list(QUERIES),
        "strictTypeScript": True,
        "runtimeEnvelopeChecks": True,
        "arbitraryCodeExecution": False,
        "missingOpenApiOperations": missing,
    }
