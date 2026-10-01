from __future__ import annotations
from .cross_language_entity_resolution_runtime import *
WORKSPACE_SCHEMA="sc-workspace-cross-language-entity-toponym-resolution-workspace/1.0"
WORKSPACE_VERSION="3.51.0"
def profile():
    return {"schema":WORKSPACE_SCHEMA,"version":WORKSPACE_VERSION,"title":"Cross-Language Entity & Toponym Resolution Workspace","runtimeSchema":RUNTIME_SCHEMA,"runtimeProfileEndpoint":"/v1/cross-language-entity-resolution-runtime","runtimeOperationsEndpoint":"/v1/cross-language-entity-resolution-runtime/operations","runtimeExecuteEndpoint":"/v1/cross-language-entity-resolution-runtime/execute","boundedOperations":list(OPERATIONS),"boundedOperationCount":len(OPERATIONS),"originalLanguageFirst":True,"historicalNamesPreserved":True,"automaticEntityMergeEnabled":False,"automaticTranslationEnabled":False,"provenancePreserved":True,"arbitraryCodeExecution":False,"schemas":{"request":REQUEST_SCHEMA,"result":RESULT_SCHEMA,"entity":ENTITY_SCHEMA,"nameForm":NAME_SCHEMA,"candidate":CANDIDATE_SCHEMA,"decision":DECISION_SCHEMA,"lineage":LINEAGE_SCHEMA}}
