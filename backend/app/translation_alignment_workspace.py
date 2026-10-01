from __future__ import annotations
from .translation_alignment_runtime import (
    RUNTIME_SCHEMA, OPERATIONS, REQUEST_SCHEMA, RESULT_SCHEMA,
    TRANSFORMATION_SCHEMA, SEGMENT_SCHEMA, ALIGNMENT_SCHEMA, LINEAGE_SCHEMA,
)
WORKSPACE_SCHEMA = "sc-workspace-translation-transliteration-parallel-alignment-workspace/1.0"
WORKSPACE_VERSION = "3.49.0"

def profile() -> dict:
    return {
        "schema": WORKSPACE_SCHEMA, "version": WORKSPACE_VERSION,
        "title": "Translation, Transliteration & Parallel Alignment Workspace",
        "runtimeSchema": RUNTIME_SCHEMA,
        "runtimeProfileEndpoint": "/v1/translation-alignment-runtime",
        "runtimeOperationsEndpoint": "/v1/translation-alignment-runtime/operations",
        "runtimeExecuteEndpoint": "/v1/translation-alignment-runtime/execute",
        "boundedOperations": list(OPERATIONS), "boundedOperationCount": len(OPERATIONS),
        "originalLanguageFirst": True, "translationIsDerivedRepresentation": True,
        "transliterationIsDerivedRepresentation": True,
        "automaticLanguageDetectionEnabled": False, "automaticTranslationEnabled": False,
        "automaticTransliterationEnabled": False, "automaticAlignmentEnabled": False,
        "provenancePreserved": True, "arbitraryCodeExecution": False,
        "schemas":{"request":REQUEST_SCHEMA,"result":RESULT_SCHEMA,"transformation":TRANSFORMATION_SCHEMA,
                   "segment":SEGMENT_SCHEMA,"alignment":ALIGNMENT_SCHEMA,"lineage":LINEAGE_SCHEMA},
    }
