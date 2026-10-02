from __future__ import annotations
from .model_registry_lineage_runtime import *

WORKSPACE_SCHEMA="sc-workspace-model-registry-lineage-workspace/1.0"
WORKSPACE_VERSION="3.59.0"

def profile():
    return {
        "schema":WORKSPACE_SCHEMA,
        "version":WORKSPACE_VERSION,
        "title":"Model Registry & Research Model Lineage",
        "runtimeSchema":RUNTIME_SCHEMA,
        "runtimeProfileEndpoint":"/v1/model-registry-lineage-runtime",
        "runtimeOperationsEndpoint":"/v1/model-registry-lineage-runtime/operations",
        "runtimeExecuteEndpoint":"/v1/model-registry-lineage-runtime/execute",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "modelRegistration":True,
        "modelVersioning":True,
        "parentDerivedLineage":True,
        "datasetFeatureExperimentRunLineage":True,
        "artifactFingerprinting":True,
        "evaluationBindings":True,
        "promotionReadiness":True,
        "reproducibilityPackaging":True,
        "humanReviewRequiredForPromotion":True,
        "automaticModelPromotionEnabled":False,
        "automaticApprovalEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "arbitraryCodeExecution":False,
        "provenancePreserved":True,
        "schemas":{
            "request":REQUEST_SCHEMA,
            "result":RESULT_SCHEMA,
            "model":MODEL_SCHEMA,
            "version":VERSION_SCHEMA,
            "lineage":LINEAGE_SCHEMA,
            "evaluationBinding":EVALUATION_BINDING_SCHEMA,
            "package":PACKAGE_SCHEMA,
        },
    }
