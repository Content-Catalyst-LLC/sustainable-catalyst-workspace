from __future__ import annotations
from .cross_lingual_semantic_evidence_runtime import *

WORKSPACE_SCHEMA="sc-workspace-cross-lingual-semantic-evidence-workspace/1.0"
WORKSPACE_VERSION="3.52.0"

def profile():
    return {"schema":WORKSPACE_SCHEMA,"version":WORKSPACE_VERSION,"title":"Cross-Lingual Semantic & Evidence Workspace",
        "runtimeSchema":RUNTIME_SCHEMA,"runtimeProfileEndpoint":"/v1/cross-lingual-semantic-evidence-runtime",
        "runtimeOperationsEndpoint":"/v1/cross-lingual-semantic-evidence-runtime/operations",
        "runtimeExecuteEndpoint":"/v1/cross-lingual-semantic-evidence-runtime/execute",
        "boundedOperations":list(OPERATIONS),"boundedOperationCount":len(OPERATIONS),
        "originalLanguageFirst":True,"translationIsDerivedRepresentation":True,"historicalLanguageIdentityPreserved":True,
        "entityResolutionLineagePreserved":True,"automaticTranslationEnabled":False,
        "automaticSemanticEquivalenceEnabled":False,"automaticEvidenceRankingEnabled":False,
        "automaticTruthDeterminationEnabled":False,"humanReviewRequiredForAcceptedEquivalence":True,
        "provenancePreserved":True,"arbitraryCodeExecution":False,
        "schemas":{"request":REQUEST_SCHEMA,"result":RESULT_SCHEMA,"unit":UNIT_SCHEMA,"candidate":CANDIDATE_SCHEMA,
                   "link":LINK_SCHEMA,"evidenceMap":MAP_SCHEMA,"lineage":LINEAGE_SCHEMA}}
