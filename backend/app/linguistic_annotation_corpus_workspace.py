from __future__ import annotations

from .linguistic_annotation_runtime import (
    RUNTIME_SCHEMA,
    OPERATIONS,
    REQUEST_SCHEMA,
    RESULT_SCHEMA,
    ANNOTATION_SCHEMA,
    LAYER_SCHEMA,
    STRUCTURE_NODE_SCHEMA,
    DOCUMENT_STRUCTURE_SCHEMA,
    CORPUS_STRUCTURE_SCHEMA,
    ANNOTATION_LINEAGE_SCHEMA,
    OFFSET_UNIT,
)

WORKSPACE_SCHEMA = "sc-workspace-linguistic-annotation-corpus-structure-workspace/1.0"
WORKSPACE_VERSION = "3.48.0"


def profile() -> dict:
    return {
        "schema": WORKSPACE_SCHEMA,
        "version": WORKSPACE_VERSION,
        "title": "Linguistic Annotation & Corpus Structure Workspace",
        "runtimeSchema": RUNTIME_SCHEMA,
        "runtimeProfileEndpoint": "/v1/linguistic-annotation-runtime",
        "runtimeOperationsEndpoint": "/v1/linguistic-annotation-runtime/operations",
        "runtimeExecuteEndpoint": "/v1/linguistic-annotation-runtime/execute",
        "boundedOperations": list(OPERATIONS),
        "boundedOperationCount": len(OPERATIONS),
        "offsetUnit": OFFSET_UNIT,
        "originalLanguageFirst": True,
        "translationIsDerivedRepresentation": True,
        "automaticLanguageDetectionEnabled": False,
        "automaticTranslationEnabled": False,
        "provenancePreserved": True,
        "arbitraryCodeExecution": False,
        "schemas": {
            "request": REQUEST_SCHEMA,
            "result": RESULT_SCHEMA,
            "annotation": ANNOTATION_SCHEMA,
            "layer": LAYER_SCHEMA,
            "structureNode": STRUCTURE_NODE_SCHEMA,
            "documentStructure": DOCUMENT_STRUCTURE_SCHEMA,
            "corpusStructure": CORPUS_STRUCTURE_SCHEMA,
            "annotationLineage": ANNOTATION_LINEAGE_SCHEMA,
        },
    }
