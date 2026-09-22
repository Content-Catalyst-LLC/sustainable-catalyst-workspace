from __future__ import annotations
from typing import Any

PRODUCTION_ARCHITECTURE_CERTIFICATION_SCHEMA = "sc-workspace-production-architecture-certification/1.0"


def profile() -> dict[str, Any]:
    """Machine-readable v2.36 production-architecture certification contract.

    This certifies architectural invariants that can be verified deterministically
    from the release and a deployed backend. It deliberately does not claim that
    public-site/cache/CDN/rollback field checks have been performed.
    """
    return {
        "schema": PRODUCTION_ARCHITECTURE_CERTIFICATION_SCHEMA,
        "workspaceVersion": "3.8.0",
        "release": "Workspace Production Architecture Certification",
        "certificationScope": "automated-architecture",
        "architectureCertified": True,
        "liveProductionCertified": False,
        "liveFieldChecksRequired": True,
        "backendFirst": True,
        "backendAuthoritative": True,
        "browserAuthoritativeState": False,
        "browserAuthoritativeAuthorization": False,
        "canonicalStore": "postgresql",
        "migrationRequired": True,
        "migrationLineage": "038_claims_evidence_investigative_research_workspace.sql",
        "rollbackBaseline": "3.6.0",
        "rollbackSchemaCompatible": True,
        "serviceIdentityBoundary": "server-side-wordpress-proxy",
        "authorizationDefaultEffect": "deny",
        "runtimeExecutionBoundary": "bounded-internal-services",
        "runtimeArbitraryCodeExecution": False,
        "typedClientTransport": "wordpress-server-proxy",
        "browserDirectBackendAccess": False,
        "canonicalClientCachePersistent": False,
        "offlineOutboxAuthoritative": False,
        "syncAutomaticSemanticMerge": False,
        "scientificObjectGenericMutation": False,
        "handoffGenericDestinationMutation": False,
        "frontendPrimaryShellThin": True,
        "legacyLocalCompatibilityLazy": True,
        "serviceCredentialsBrowserVisible": False,
        "packageAssetNamesVersionDerived": True,
        "integrityAlgorithm": "SHA-256",
        "certificationGates": {
            "claimsEvidenceInvestigativeResearchWorkspace": "release-gate",
            "investigationGraphContradictionHypothesisWorkspace": "release-gate",
            "platformCoreVisualResearchWorkspace": "release-gate",
            "backendAuthority": "certified",
            "persistenceAndRevisionAuthority": "certified",
            "policyIdentityAuthorization": "certified",
            "typedClientProxyBoundary": "certified",
            "thinFrontendResponsibility": "certified",
            "localFirstSyncAuthority": "certified",
            "scientificObjectBoundary": "certified",
            "crossProductHandoffBoundary": "certified",
            "platformCoreV3RuntimeIntegration": "release-gate",
            "scientificExecutionProvenance": "release-gate",
            "boundedRuntimeIsolation": "deployment-gate",
            "wordpressPackageIntegrity": "release-gate",
            "releaseReconstruction": "release-gate",
            "livePublicPageSmoke": "manual-pending",
            "liveCacheCoherence": "manual-pending",
            "liveRollbackRehearsal": "manual-pending",
        },
    }
