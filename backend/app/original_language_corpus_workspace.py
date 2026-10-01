from __future__ import annotations

from .multilingual_corpus_runtime import (
    RUNTIME_SCHEMA,
    OPERATIONS,
    REQUEST_SCHEMA,
    RESULT_SCHEMA,
    TEXT_IDENTITY_SCHEMA,
    SEGMENT_SCHEMA,
    CORPUS_PROFILE_SCHEMA,
    TRANSFORMATION_PROVENANCE_SCHEMA,
)

WORKSPACE_SCHEMA = "sc-workspace-original-language-corpus-workspace/1.0"
WORKSPACE_VERSION = "3.47.0"


def profile() -> dict:
    return {
        "schema": WORKSPACE_SCHEMA,
        "version": WORKSPACE_VERSION,
        "title": "Original-Language Text & Corpus Workspace Foundation",
        "runtimeSchema": RUNTIME_SCHEMA,
        "runtimeProfileEndpoint": "/v1/multilingual-text-corpus-runtime",
        "runtimeOperationsEndpoint": "/v1/multilingual-text-corpus-runtime/operations",
        "runtimeExecuteEndpoint": "/v1/multilingual-text-corpus-runtime/execute",
        "boundedOperations": list(OPERATIONS),
        "boundedOperationCount": len(OPERATIONS),
        "originalLanguageFirst": True,
        "translationIsDerivedRepresentation": True,
        "transliterationIsDerivedRepresentation": True,
        "automaticLanguageDetectionEnabled": False,
        "automaticTranslationEnabled": False,
        "automaticTransliterationEnabled": False,
        "languageMetadataRequired": True,
        "arbitraryCodeExecution": False,
        "schemas": {
            "request": REQUEST_SCHEMA,
            "result": RESULT_SCHEMA,
            "textIdentity": TEXT_IDENTITY_SCHEMA,
            "segment": SEGMENT_SCHEMA,
            "corpusProfile": CORPUS_PROFILE_SCHEMA,
            "transformationProvenance": TRANSFORMATION_PROVENANCE_SCHEMA,
        },
    }
