from __future__ import annotations
from .dataset_feature_engineering_runtime import *

WORKSPACE_SCHEMA="sc-workspace-dataset-feature-engineering-workspace/1.0"
WORKSPACE_VERSION="3.57.0"

def profile():
    return {
        "schema":WORKSPACE_SCHEMA,
        "version":WORKSPACE_VERSION,
        "title":"Dataset & Feature Engineering Workspace",
        "runtimeSchema":RUNTIME_SCHEMA,
        "runtimeProfileEndpoint":"/v1/dataset-feature-engineering-runtime",
        "runtimeOperationsEndpoint":"/v1/dataset-feature-engineering-runtime/operations",
        "runtimeExecuteEndpoint":"/v1/dataset-feature-engineering-runtime/execute",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "datasetProfiling":True,
        "featureCatalog":True,
        "transformationPlanning":True,
        "featureLineage":True,
        "leakageRiskInspection":True,
        "reproducibilityPackaging":True,
        "automaticFeatureSelectionEnabled":False,
        "automaticTransformationExecutionEnabled":False,
        "automaticLeakageOverrideEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "arbitraryCodeExecution":False,
        "provenancePreserved":True,
        "schemas":{
            "request":REQUEST_SCHEMA,
            "result":RESULT_SCHEMA,
            "dataset":DATASET_SCHEMA,
            "feature":FEATURE_SCHEMA,
            "transformation":TRANSFORM_SCHEMA,
            "lineage":LINEAGE_SCHEMA,
            "package":PACKAGE_SCHEMA,
        },
    }
