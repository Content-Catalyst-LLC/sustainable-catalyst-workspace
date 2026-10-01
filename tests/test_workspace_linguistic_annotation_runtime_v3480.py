from backend.app.linguistic_annotation_runtime import (
    LinguisticAnnotationRuntimeRequest,
    execute,
    OPERATIONS,
)


def payload(operation):
    return LinguisticAnnotationRuntimeRequest.model_validate({
        "schema": "sc-workspace-linguistic-annotation-runtime-request/1.0",
        "operation": operation,
        "documents": [{
            "documentId": "d1",
            "text": "Hello world.",
            "languageTag": "en",
            "script": "Latn",
            "representation": "original",
        }],
        "layers": [
            {
                "layerId": "tokens",
                "title": "Tokens",
                "annotationType": "token",
                "annotationIds": ["a1"],
            },
            {
                "layerId": "entities",
                "title": "Entities",
                "annotationType": "entity",
                "annotationIds": ["a2"],
            },
        ],
        "annotations": [
            {
                "annotationId": "a1",
                "documentId": "d1",
                "layerId": "tokens",
                "annotationType": "token",
                "startOffset": 0,
                "endOffset": 5,
                "label": "TOKEN",
                "method": "human",
            },
            {
                "annotationId": "a2",
                "documentId": "d1",
                "layerId": "entities",
                "annotationType": "entity",
                "startOffset": 0,
                "endOffset": 5,
                "label": "GREETING",
                "method": "model",
                "confidence": 0.9,
                "derivedFromAnnotationIds": ["a1"],
            },
        ],
        "structureNodes": [
            {
                "nodeId": "n1",
                "documentId": "d1",
                "nodeType": "document",
                "order": 0,
                "startOffset": 0,
                "endOffset": 12,
            },
            {
                "nodeId": "n2",
                "documentId": "d1",
                "nodeType": "sentence",
                "parentId": "n1",
                "order": 0,
                "startOffset": 0,
                "endOffset": 12,
            },
        ],
        "targetDocumentId": "d1",
    })


def test_all_bounded_operations():
    for operation in OPERATIONS:
        result = execute(payload(operation))
        assert result["operation"] == operation
        assert result["policy"]["originalLanguageFirst"] is True
        assert result["policy"]["automaticTranslationEnabled"] is False
        assert result["policy"]["offsetUnit"] == "unicode-code-point"


def test_span_index_extracts_text():
    result = execute(payload("workspace.linguistics.annotation-span-index"))
    assert result["result"]["items"][0]["text"] == "Hello"


def test_annotation_lineage_preserved():
    result = execute(payload("workspace.linguistics.annotation-lineage"))
    assert result["result"]["edgeCount"] == 1
    assert result["result"]["edges"][0]["fromAnnotationId"] == "a1"
    assert result["result"]["edges"][0]["toAnnotationId"] == "a2"
