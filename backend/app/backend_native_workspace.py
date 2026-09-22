from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from .authorization import principal_payload
from .cross_product_handoffs import profile as handoff_profile
from .frontend_runtime import profile as frontend_runtime_profile
from .local_first_sync import profile as sync_profile, bootstrap as sync_bootstrap
from .production_certification import profile as production_certification_profile
from .scientific_objects import profile as scientific_object_profile
from .thin_client_state import profile as thin_client_profile, bootstrap as thin_client_bootstrap
from .platform_core_runtime import profile as platform_core_runtime_profile
from .research_session_bindings import profile as research_session_binding_profile
from .execution_provenance import profile as execution_provenance_profile
from .investigative_research_workspace import profile as investigative_research_profile
from .utils import sha256_hex

BACKEND_NATIVE_WORKSPACE_SCHEMA = "sc-workspace-backend-native-scientific-workspace/1.0"
BACKEND_NATIVE_BOOTSTRAP_SCHEMA = "sc-workspace-backend-native-scientific-workspace-bootstrap/1.0"


def profile() -> dict[str, Any]:
    return {
        "schema": BACKEND_NATIVE_WORKSPACE_SCHEMA,
        "workspaceVersion": "3.5.0",
        "release": "Claims, Evidence & Investigative Research Workspace",
        "architectureGeneration": 3,
        "backendNative": True,
        "backendFirst": True,
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "browserAuthoritativeAuthorization": False,
        "canonicalStore": "postgresql",
        "canonicalDomainRuntime": "python",
        "canonicalReads": "server-generated-read-models",
        "canonicalWrites": "bounded-backend-commands-and-domain-apis",
        "canonicalClientCache": "memory-only-rehydratable",
        "canonicalClientCachePersistent": False,
        "signedInLocalCanonicalFallback": False,
        "guestLocalCompatibility": True,
        "guestLocalCompatibilityAuthoritativeScope": "browser-local-projects-only",
        "offlineOutboxAuthoritative": False,
        "syncAutomaticSemanticMerge": False,
        "scientificObjectGenericMutation": False,
        "handoffGenericDestinationMutation": False,
        "scientificExecutionAuthority": "bounded-internal-runtime-services",
        "runtimeArbitraryCodeExecution": False,
        "typedClientTransport": "wordpress-server-proxy",
        "browserDirectBackendAccess": False,
        "serviceCredentialsBrowserVisible": False,
        "serverResolvedIdentity": True,
        "authorizationDefaultEffect": "deny",
        "durableProvenanceAndReceipts": True,
        "reproducibleStudyPackages": True,
        "rendererNeutralVisualizationSpecifications": True,
        "crossProductResearchHandoffs": True,
        "migrationRequired": True,
        "migrationLineage": "038_claims_evidence_investigative_research_workspace.sql",
        "rollbackBaseline": "3.6.0",
        "platformCoreV3UnifiedResearchRuntimeIntegration": True,
        "researchSessionObjectBindingRuntime": True,
        "scientificExecutionProvenanceWorkspace": True,
        "platformCoreVisualAnalysisResearchObjectWorkspace": True,
        "claimsEvidenceInvestigativeResearchWorkspace": True,
        "platformCoreReferenceFirst": True,
        "rollbackSchemaCompatible": True,
        "bootstrapEndpoint": "/v1/backend-native-workspace/bootstrap",
        "requiredSubsystems": [
            "authorization", "thin-client-state", "local-first-sync",
            "scientific-objects", "cross-product-handoffs",
            "notebook-artifact-orchestration", "scientific-study-packages",
            "visualization-specifications", "bounded-scientific-runtimes",
            "platform-core-v3-unified-research-runtime", "research-session-object-bindings", "scientific-execution-provenance", "visual-research", "investigative-research"
        ],
    }


def bootstrap(db: Session, identity: Any, project_id: str | None = None) -> dict[str, Any]:
    thin = thin_client_bootstrap(db, identity.user_key, project_id)
    sync = sync_bootstrap(db, identity.user_key)
    principal = principal_payload(identity)
    authority = {
        "principal": principal,
        "thinClient": thin_client_profile(),
        "sync": sync_profile(),
        "scientificObjects": scientific_object_profile(),
        "handoffs": handoff_profile(),
        "frontend": frontend_runtime_profile(),
        "productionArchitecture": production_certification_profile(),
        "platformCoreRuntime": platform_core_runtime_profile(),
        "researchSessionBindings": research_session_binding_profile(),
        "executionProvenance": execution_provenance_profile(),
        "investigativeResearch": investigative_research_profile(),
    }
    canonical = {
        "thinClient": thin,
        "sync": sync,
    }
    fingerprint_basis = {
        "workspaceVersion": "3.5.0",
        "principalId": principal.get("principalId", ""),
        "authority": authority,
        "canonicalProjectionFingerprint": thin.get("projectionFingerprint", ""),
        "syncCheckpoint": sync.get("checkpoint", ""),
    }
    return {
        "schema": BACKEND_NATIVE_BOOTSTRAP_SCHEMA,
        "workspaceVersion": "3.5.0",
        "backendNative": True,
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "browserAuthoritativeAuthorization": False,
        "projectId": project_id or "",
        "authority": authority,
        "canonical": canonical,
        "sessionFingerprint": sha256_hex(fingerprint_basis),
        "clientPolicy": {
            "persistCanonicalCache": False,
            "persistTransientStateOnly": True,
            "mutateCanonicalStateThroughBackendOnly": True,
            "rehydrateAfterMutationOrConflict": True,
            "allowSignedInLocalCanonicalFallback": False,
            "allowGuestBrowserLocalProjects": True,
        },
    }
