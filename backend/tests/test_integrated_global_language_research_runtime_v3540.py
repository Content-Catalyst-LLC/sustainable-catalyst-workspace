from app.integrated_global_language_research_runtime import (
    IntegratedGlobalLanguageResearchRequest,
    execute,
    operation_catalog,
    profile,
)

def request(operation):
    kinds=[
        "original-language-corpus",
        "linguistic-annotation",
        "translation-alignment",
        "historical-language-identity",
        "entity-toponym-resolution",
        "cross-lingual-semantic-evidence",
        "reproducible-computational-linguistics",
    ]
    return IntegratedGlobalLanguageResearchRequest.model_validate({
        "operation":operation,
        "projectId":"global-1",
        "title":"Global language research",
        "layers":[{
            "layerId":f"layer-{i}",
            "layerKind":kind,
            "objectRefs":[f"object:{i}"],
            "sourceRefs":[] if kind=="reproducible-computational-linguistics" else [f"source:{i}"],
            "lineageRefs":[f"prior:{i}"],
        } for i,kind in enumerate(kinds)],
        "evidenceRelations":[{
            "relationId":"rel-1",
            "sourceRef":"object:0",
            "targetRef":"object:5",
            "relationType":"supports",
            "confidence":0.8,
            "sourceRefs":["source:0","source:5"],
            "humanReviewed":True,
        }],
        "sourceAssessments":[{
            "sourceRef":"source:0",
            "qualitySignals":{"provenance":"documented"},
            "userTrustState":"trusted",
            "userTrustReason":"User-selected.",
        }],
    })

def test_profile():
    p=profile()
    assert p["version"]=="3.54.0"
    assert p["boundedOperationCount"]==7
    assert p["sourceQualitySignalsSeparatedFromUserTrust"] is True
    assert p["arbitraryCodeExecution"] is False

def test_catalog():
    rows=operation_catalog()
    assert len(rows)==7
    assert all(x["bounded"] for x in rows)

def test_readiness():
    r=execute(request("workspace.linguistics.global-language-readiness"))
    assert r["result"]["ready"] is True
    assert r["result"]["presentRequiredLayerCount"]==7

def test_trust_separation():
    r=execute(request("workspace.linguistics.source-quality-user-trust-view"))
    assert r["result"]["sourceQualitySignalsSeparatedFromUserTrust"] is True
    assert r["result"]["automaticTrustDecisionEnabled"] is False

def test_package():
    r=execute(request("workspace.linguistics.global-language-research-package"))
    assert len(r["result"]["packageSha256"])==64
    assert r["result"]["originalLanguageFirst"] is True
