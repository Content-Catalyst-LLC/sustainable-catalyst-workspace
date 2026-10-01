from __future__ import annotations
from .integrated_global_language_research_runtime import *

WORKSPACE_SCHEMA="sc-workspace-integrated-global-language-research-workspace/1.0"
WORKSPACE_VERSION="3.54.0"

def profile():
    return {
        "schema":WORKSPACE_SCHEMA,
        "version":WORKSPACE_VERSION,
        "title":"Integrated Global Language Research Workspace",
        "runtimeSchema":RUNTIME_SCHEMA,
        "runtimeProfileEndpoint":"/v1/integrated-global-language-research-runtime",
        "runtimeOperationsEndpoint":"/v1/integrated-global-language-research-runtime/operations",
        "runtimeExecuteEndpoint":"/v1/integrated-global-language-research-runtime/execute",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "integratedLanguageResearchLayers":list(REQUIRED_LAYERS),
        "originalLanguageFirst":True,
        "translationIsDerivedRepresentation":True,
        "historicalLanguageIdentityPreserved":True,
        "crossCivilizationalEvidenceLinking":True,
        "sourceQualitySignalsSeparatedFromUserTrust":True,
        "automaticTranslationEnabled":False,
        "automaticEntityMergeEnabled":False,
        "automaticSemanticEquivalenceEnabled":False,
        "automaticEvidenceRankingEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "automaticPublicationEnabled":False,
        "humanReviewRequired":True,
        "provenancePreserved":True,
        "arbitraryCodeExecution":False,
        "schemas":{
            "request":REQUEST_SCHEMA,
            "result":RESULT_SCHEMA,
            "project":PROJECT_SCHEMA,
            "layer":LAYER_SCHEMA,
            "evidenceView":EVIDENCE_VIEW_SCHEMA,
            "trustView":TRUST_VIEW_SCHEMA,
            "lineage":LINEAGE_SCHEMA,
            "package":PACKAGE_SCHEMA,
        },
    }
