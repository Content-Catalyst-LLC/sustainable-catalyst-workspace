from app.model_registry_lineage_runtime import ModelRegistryLineageRequest, execute, operation_catalog, profile

def req(operation):
    return ModelRegistryLineageRequest.model_validate({
        "operation":operation,
        "registryId":"registry-1",
        "modelId":"model-1",
        "title":"Research model",
        "modelKind":"predictive-model",
        "sourceRefs":["source:1"],
        "modelVersions":[
            {
                "modelVersionId":"model-1:v1",
                "modelRef":"model-1",
                "datasetRef":"dataset:1",
                "featurePackageRef":"features:1",
                "experimentRef":"experiment:1",
                "runRef":"run:1",
                "environmentRef":"env:1",
                "artifactRefs":["artifact:model-v1"],
                "artifactSha256":{"artifact:model-v1":"a"*64},
                "provenanceRefs":["prov:model-v1"],
                "authorRefs":["author:1"],
                "status":"candidate"
            }
        ],
        "evaluationBindings":[
            {
                "bindingId":"eval-1",
                "modelVersionId":"model-1:v1",
                "experimentRef":"experiment:1",
                "runRef":"run:1",
                "metricValues":{"accuracy":0.82},
                "evaluationArtifactRefs":["artifact:eval-1"],
                "provenanceRefs":["prov:eval-1"]
            }
        ]
    })

def test_profile():
    p=profile()
    assert p["version"]=="3.59.0"
    assert p["boundedOperationCount"]==7
    assert p["automaticModelPromotionEnabled"] is False
    assert p["arbitraryCodeExecution"] is False

def test_catalog_bounded():
    rows=operation_catalog()
    assert len(rows)==7
    assert all(x["bounded"] for x in rows)

def test_register():
    r=execute(req("workspace.models.register"))
    assert r["result"]["modelId"]=="model-1"
    assert len(r["result"]["registryFingerprint"])==64

def test_lineage():
    r=execute(req("workspace.models.lineage-graph"))
    assert r["result"]["datasetFeatureExperimentRunLineagePreserved"] is True

def test_promotion_readiness():
    r=execute(req("workspace.models.promotion-readiness"))
    assert r["result"]["items"][0]["readyForHumanReview"] is True
    assert r["result"]["automaticModelPromotionEnabled"] is False

def test_package():
    r=execute(req("workspace.models.reproducibility-package"))
    assert len(r["result"]["packageSha256"])==64
