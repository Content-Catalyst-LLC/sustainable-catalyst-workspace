from __future__ import annotations

from .historical_language_identity_runtime import (
    RUNTIME_SCHEMA,
    OPERATIONS,
    REQUEST_SCHEMA,
    RESULT_SCHEMA,
    LANGUAGE_IDENTITY_SCHEMA,
    SCRIPT_IDENTITY_SCHEMA,
    VARIANT_SCHEMA,
    RELATION_SCHEMA,
    LINEAGE_SCHEMA,
)

WORKSPACE_SCHEMA = "sc-workspace-historical-language-script-variant-identity-workspace/1.0"
WORKSPACE_VERSION = "3.50.0"


def profile() -> dict:
    return {
        "schema": WORKSPACE_SCHEMA,
        "version": WORKSPACE_VERSION,
        "title": "Historical Language, Script & Variant Identity Workspace",
        "runtimeSchema": RUNTIME_SCHEMA,
        "runtimeProfileEndpoint": "/v1/historical-language-identity-runtime",
        "runtimeOperationsEndpoint": "/v1/historical-language-identity-runtime/operations",
        "runtimeExecuteEndpoint": "/v1/historical-language-identity-runtime/execute",
        "boundedOperations": list(OPERATIONS),
        "boundedOperationCount": len(OPERATIONS),
        "originalLanguageFirst": True,
        "historicalIdentityPreserved": True,
        "automaticLanguageDetectionEnabled": False,
        "automaticModernizationEnabled": False,
        "automaticVariantNormalizationEnabled": False,
        "automaticTranslationEnabled": False,
        "provenancePreserved": True,
        "arbitraryCodeExecution": False,
        "schemas": {
            "request": REQUEST_SCHEMA,
            "result": RESULT_SCHEMA,
            "languageIdentity": LANGUAGE_IDENTITY_SCHEMA,
            "scriptIdentity": SCRIPT_IDENTITY_SCHEMA,
            "variant": VARIANT_SCHEMA,
            "relation": RELATION_SCHEMA,
            "lineage": LINEAGE_SCHEMA,
        },
    }
