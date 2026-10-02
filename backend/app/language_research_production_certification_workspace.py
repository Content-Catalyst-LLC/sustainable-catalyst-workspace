from __future__ import annotations
from .language_research_production_certification_runtime import *

WORKSPACE_SCHEMA="sc-workspace-language-research-production-certification-workspace/1.0"
WORKSPACE_VERSION="3.55.0"

def profile():
    return {
        "schema":WORKSPACE_SCHEMA,
        "version":WORKSPACE_VERSION,
        "title":"Language Research Production Certification",
        "runtimeSchema":RUNTIME_SCHEMA,
        "runtimeProfileEndpoint":"/v1/language-research-production-certification-runtime",
        "runtimeOperationsEndpoint":"/v1/language-research-production-certification-runtime/operations",
        "runtimeExecuteEndpoint":"/v1/language-research-production-certification-runtime/execute",
        "certifiesWorkspaceVersions":["3.47.0","3.48.0","3.49.0","3.50.0","3.51.0","3.52.0","3.53.0","3.54.0"],
        "requiredLayers":list(REQUIRED_LAYERS),
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "productionCertification":True,
        "originalLanguageFirst":True,
        "translationIsDerivedRepresentation":True,
        "provenancePreserved":True,
        "humanReviewRequired":True,
        "sourceQualitySignalsSeparatedFromUserTrust":True,
        "automaticTruthDeterminationEnabled":False,
        "automaticEvidenceRankingEnabled":False,
        "automaticPublicationEnabled":False,
        "arbitraryCodeExecution":False,
        "schemas":{"request":REQUEST_SCHEMA,"result":RESULT_SCHEMA,"report":REPORT_SCHEMA,"package":PACKAGE_SCHEMA},
    }
