from backend.app.historical_language_identity_runtime import (
    HistoricalLanguageIdentityRuntimeRequest,
    OPERATIONS,
    execute,
)


def req(operation):
    return HistoricalLanguageIdentityRuntimeRequest.model_validate({
        "schema": "sc-workspace-historical-language-identity-runtime-request/1.0",
        "operation": operation,
        "languageIdentities": [
            {
                "identityId": "enm",
                "label": "Middle English",
                "kind": "historical-stage",
                "languageTag": "enm",
                "scriptIds": ["latn"],
                "regions": ["England"],
                "temporalScope": {"startYear": 1100, "endYear": 1500, "approximate": True},
            },
            {
                "identityId": "en",
                "label": "Modern English",
                "kind": "language",
                "languageTag": "en",
                "scriptIds": ["latn"],
                "temporalScope": {"startYear": 1500, "approximate": True},
            },
        ],
        "scriptIdentities": [
            {
                "scriptId": "latn",
                "label": "Latin script",
                "scriptCode": "Latn",
                "direction": "ltr",
            }
        ],
        "variants": [
            {
                "variantId": "enm-orth",
                "label": "Middle English orthographic variety",
                "kind": "orthography",
                "languageIdentityId": "enm",
                "scriptIdentityId": "latn",
                "temporalScope": {"startYear": 1300, "endYear": 1500, "approximate": True},
            }
        ],
        "relations": [
            {
                "relationId": "r1",
                "fromId": "enm",
                "toId": "en",
                "relationType": "predecessor-of",
                "confidence": 0.95,
            }
        ],
    })


def test_all_operations():
    for operation in OPERATIONS:
        result = execute(req(operation))
        assert result["operation"] == operation
        assert result["policy"]["originalLanguageFirst"] is True
        assert result["policy"]["historicalIdentityPreserved"] is True
        assert result["policy"]["automaticModernizationEnabled"] is False


def test_variant_index_and_lineage():
    index = execute(req("workspace.linguistics.historical-variant-index"))["result"]
    assert index["count"] == 1
    lineage = execute(req("workspace.linguistics.historical-identity-lineage"))["result"]
    assert lineage["edgeCount"] == 1
    assert lineage["historicalIdentityPreserved"] is True
