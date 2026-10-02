from __future__ import annotations
from .research_pipeline_composer_runtime import *

WORKSPACE_SCHEMA="sc-workspace-research-pipeline-composer-workspace/1.0"
WORKSPACE_VERSION="3.56.0"

def profile():
    return {
        "schema":WORKSPACE_SCHEMA,
        "version":WORKSPACE_VERSION,
        "title":"Research Pipeline Composer",
        "runtimeSchema":RUNTIME_SCHEMA,
        "runtimeProfileEndpoint":"/v1/research-pipeline-composer-runtime",
        "runtimeOperationsEndpoint":"/v1/research-pipeline-composer-runtime/operations",
        "runtimeExecuteEndpoint":"/v1/research-pipeline-composer-runtime/execute",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "dependencyAware":True,
        "boundedHandoffs":True,
        "crossRuntimeLineagePreserved":True,
        "reproducibilityPackaging":True,
        "humanReviewSupported":True,
        "automaticExecutionEnabled":False,
        "automaticHandoffAcceptanceEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "automaticEvidenceRankingEnabled":False,
        "arbitraryCodeExecution":False,
        "provenancePreserved":True,
        "schemas":{
            "request":REQUEST_SCHEMA,
            "result":RESULT_SCHEMA,
            "pipeline":PIPELINE_SCHEMA,
            "step":STEP_SCHEMA,
            "handoff":HANDOFF_SCHEMA,
            "plan":PLAN_SCHEMA,
            "lineage":LINEAGE_SCHEMA,
            "package":PACKAGE_SCHEMA,
        },
    }
