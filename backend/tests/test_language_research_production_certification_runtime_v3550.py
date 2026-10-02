from app.language_research_production_certification_runtime import (
    LanguageResearchProductionCertificationRequest,
    execute,
    operation_catalog,
    profile,
)

def request(operation):
    layers=[
        "original-language-corpus","linguistic-annotation","translation-alignment",
        "historical-language-identity","entity-toponym-resolution",
        "cross-lingual-semantic-evidence","reproducible-computational-linguistics",
        "integrated-global-language-research",
    ]
    return LanguageResearchProductionCertificationRequest.model_validate({
        "operation":operation,
        "releaseVersion":"3.55.0",
        "targets":[
            {"component":"backend","version":"3.55.0"},
            {"component":"wordpress","version":"3.55.0"},
        ],
        "layers":[{"layerKind":x,"available":True,"sourceRefs":["source:1"],"lineageRefs":["lineage:1"]} for x in layers],
        "deployment":{
            "backendHealthOk":True,
            "backendVersion":"3.55.0",
            "persistence":"postgresql",
            "workerVersion":"3.55.0",
            "wordpressVersion":"3.55.0",
            "authenticatedProfileOk":True,
            "operationCatalogOk":True,
            "packageIntegrityOk":True,
        },
    })

def test_profile():
    p=profile()
    assert p["version"]=="3.55.0"
    assert p["boundedOperationCount"]==7
    assert p["arbitraryCodeExecution"] is False

def test_catalog_bounded():
    rows=operation_catalog()
    assert len(rows)==7
    assert all(x["bounded"] for x in rows)

def test_layer_continuity():
    r=execute(request("workspace.linguistics.language-layer-continuity-check"))
    assert r["result"]["pass"] is True
    assert r["result"]["presentRequiredLayerCount"]==8

def test_guardrails():
    r=execute(request("workspace.linguistics.provenance-guardrail-check"))
    assert r["result"]["pass"] is True

def test_package_certified():
    r=execute(request("workspace.linguistics.production-certification-package"))
    assert r["result"]["certified"] is True
    assert len(r["result"]["packageSha256"])==64
