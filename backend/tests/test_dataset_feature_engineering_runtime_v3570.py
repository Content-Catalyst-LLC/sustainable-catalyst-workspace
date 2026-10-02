from app.dataset_feature_engineering_runtime import DatasetFeatureEngineeringRequest, execute, operation_catalog, profile

def req(operation):
    return DatasetFeatureEngineeringRequest.model_validate({
        "operation":operation,
        "datasetId":"dataset-1",
        "datasetVersion":"1",
        "sourceRefs":["source:1"],
        "rowCount":1000,
        "columnCount":3,
        "targetFeatureId":"target",
        "splitStrategy":"train-test",
        "randomSeed":42,
        "features":[
            {"featureId":"age","sourceFields":["age"],"dataType":"float"},
            {"featureId":"income","sourceFields":["income"],"dataType":"float"},
            {"featureId":"target","sourceFields":["target"],"dataType":"int","semanticRole":"target"},
        ],
        "transformations":[
            {"transformationId":"scale-age","operation":"standardize","inputFeatures":["age"],"outputFeatures":["age_scaled"],"deterministic":True,"provenanceRefs":["prov:1"]}
        ],
    })

def test_profile():
    p=profile()
    assert p["version"]=="3.57.0"
    assert p["boundedOperationCount"]==7
    assert p["arbitraryCodeExecution"] is False

def test_catalog_bounded():
    rows=operation_catalog()
    assert len(rows)==7
    assert all(x["bounded"] for x in rows)

def test_dataset_profile():
    r=execute(req("workspace.features.dataset-profile"))
    assert r["result"]["datasetId"]=="dataset-1"
    assert len(r["result"]["datasetFingerprint"])==64

def test_readiness():
    r=execute(req("workspace.features.readiness-check"))
    assert r["result"]["ready"] is True

def test_package():
    r=execute(req("workspace.features.reproducibility-package"))
    assert r["result"]["ready"] is True
    assert len(r["result"]["packageSha256"])==64
