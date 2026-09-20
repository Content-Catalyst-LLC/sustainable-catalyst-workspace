from __future__ import annotations
from typing import Any

FRONTEND_RUNTIME_SCHEMA = "sc-workspace-frontend-runtime-policy/1.0"

def profile() -> dict[str, Any]:
    return {
        "schema": FRONTEND_RUNTIME_SCHEMA,
        "workspaceVersion": "2.35.0",
        "mode": "thin-shell-with-browser-local-compatibility",
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "browserAuthoritativeAuthorization": False,
        "primaryBrowserResponsibilities": [
            "presentation", "interaction-routing", "transient-ui-state", "explicit-local-draft-outbox"
        ],
        "forbiddenBrowserAuthorities": [
            "scientific-object-semantics", "canonical-state", "authorization",
            "revision-conflict-resolution", "handoff-validation", "scientific-execution", "provenance-authority"
        ],
        "canonicalReads": "server-read-models",
        "canonicalWrites": "bounded-backend-commands",
        "canonicalCache": "memory-only-rehydratable",
        "persistentBrowserState": "transient-and-explicit-drafts-only",
        "legacyLocalCompatibility": True,
        "legacyCompatibilityMode": "lazy-browser-local-only",
        "legacyCompatibilityAuthoritative": False,
        "historicalVersionedFrontendAssetsRetired": True,
        "activeShell": "workspace-v2.35.0.js",
        "localCompatibilityBundle": "sc-workspace-local-project-compat-v2350.js",
        "packageAssetNamesVersionDerived": True,
        "serviceCredentialsBrowserVisible": False,
        "arbitraryCodeExecution": False,
    }
