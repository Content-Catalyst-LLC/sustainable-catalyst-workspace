from __future__ import annotations
from .reproducible_computational_linguistics_runtime import *

WORKSPACE_SCHEMA="sc-workspace-reproducible-computational-linguistics-workspace/1.0"
WORKSPACE_VERSION="3.53.0"

def profile():
    return {
        "schema":WORKSPACE_SCHEMA,
        "version":WORKSPACE_VERSION,
        "title":"Reproducible Computational Linguistics Workspace",
        "runtimeSchema":RUNTIME_SCHEMA,
        "runtimeProfileEndpoint":"/v1/reproducible-computational-linguistics-runtime",
        "runtimeOperationsEndpoint":"/v1/reproducible-computational-linguistics-runtime/operations",
        "runtimeExecuteEndpoint":"/v1/reproducible-computational-linguistics-runtime/execute",
        "boundedOperations":list(OPERATIONS),
        "boundedOperationCount":len(OPERATIONS),
        "originalLanguageFirst":True,
        "translationIsDerivedRepresentation":True,
        "historicalLanguageIdentityPreserved":True,
        "sourceAndTransformationLineageRequired":True,
        "runtimeIdentityCaptured":True,
        "dependencyLockCaptured":True,
        "randomSeedCaptured":True,
        "automaticTranslationEnabled":False,
        "automaticModelSelectionEnabled":False,
        "automaticTruthDeterminationEnabled":False,
        "automaticEvidenceRankingEnabled":False,
        "automaticReproductionExecution":False,
        "humanReviewRequired":True,
        "provenancePreserved":True,
        "arbitraryCodeExecution":False,
        "schemas":{
            "request":REQUEST_SCHEMA,
            "result":RESULT_SCHEMA,
            "corpusSnapshot":CORPUS_SNAPSHOT_SCHEMA,
            "pipeline":PIPELINE_SCHEMA,
            "run":RUN_SCHEMA,
            "binding":BINDING_SCHEMA,
            "package":PACKAGE_SCHEMA,
        },
    }
