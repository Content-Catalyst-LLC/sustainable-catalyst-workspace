from __future__ import annotations
from .training_evaluation_experiment_runtime import *

WORKSPACE_SCHEMA="sc-workspace-training-evaluation-experiment-workspace/1.0"
WORKSPACE_VERSION="3.58.0"

def profile():
    return {
        "schema":WORKSPACE_SCHEMA,
        "version":WORKSPACE_VERSION,
        "title":"Training & Evaluation Experiment Workspace",
        "runtimeSchema":RUNTIME_SCHEMA,
        "runtimeProfileEndpoint":"/v1/training-evaluation-experiment-runtime",
        "runtimeOperationsEndpoint":"/v1/training-evaluation-experiment-runtime/operations",
        "runtimeExecuteEndpoint":"/v1/training-evaluation-experiment-runtime/execute",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "experimentDefinitions":True,
        "trainingPlanning":True,
        "evaluationPlanning":True,
        "metricRegistry":True,
        "runLineage":True,
        "comparisonReadiness":True,
        "reproducibilityPackaging":True,
        "automaticTrainingExecutionEnabled":False,
        "automaticWinnerSelectionEnabled":False,
        "automaticModelPromotionEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "arbitraryCodeExecution":False,
        "provenancePreserved":True,
        "schemas":{
            "request":REQUEST_SCHEMA,
            "result":RESULT_SCHEMA,
            "experiment":EXPERIMENT_SCHEMA,
            "run":RUN_SCHEMA,
            "metric":METRIC_SCHEMA,
            "lineage":LINEAGE_SCHEMA,
            "package":PACKAGE_SCHEMA,
        },
    }
