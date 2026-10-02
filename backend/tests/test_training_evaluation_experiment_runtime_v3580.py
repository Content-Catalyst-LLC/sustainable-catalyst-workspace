from app.training_evaluation_experiment_runtime import TrainingEvaluationExperimentRequest, execute, operation_catalog, profile

def req(operation):
    return TrainingEvaluationExperimentRequest.model_validate({
        "operation":operation,
        "experimentId":"experiment-1",
        "title":"Baseline comparison",
        "objective":"Compare two model configurations reproducibly.",
        "datasetRef":"dataset:1",
        "featurePackageRef":"features:1",
        "modelRefs":["model:a","model:b"],
        "splitStrategy":"train-validation-test",
        "randomSeed":42,
        "sourceRefs":["source:1"],
        "metrics":[
            {"metricId":"accuracy","name":"Accuracy","direction":"maximize","split":"test"}
        ],
        "runs":[
            {"runId":"run-a","modelRef":"model:a","datasetRef":"dataset:1","featurePackageRef":"features:1","environmentRef":"env:1","randomSeed":42,"metricValues":{"accuracy":0.8},"provenanceRefs":["prov:a"]},
            {"runId":"run-b","modelRef":"model:b","datasetRef":"dataset:1","featurePackageRef":"features:1","environmentRef":"env:1","randomSeed":42,"metricValues":{"accuracy":0.82},"provenanceRefs":["prov:b"]},
        ],
    })

def test_profile():
    p=profile()
    assert p["version"]=="3.58.0"
    assert p["boundedOperationCount"]==7
    assert p["automaticWinnerSelectionEnabled"] is False
    assert p["arbitraryCodeExecution"] is False

def test_catalog_bounded():
    rows=operation_catalog()
    assert len(rows)==7
    assert all(x["bounded"] for x in rows)

def test_experiment_profile():
    r=execute(req("workspace.experiments.experiment-profile"))
    assert r["result"]["experimentId"]=="experiment-1"
    assert len(r["result"]["experimentFingerprint"])==64

def test_comparison_readiness():
    r=execute(req("workspace.experiments.comparison-readiness"))
    assert r["result"]["ready"] is True
    assert r["result"]["runCount"]==2

def test_package():
    r=execute(req("workspace.experiments.reproducibility-package"))
    assert r["result"]["comparisonReady"] is True
    assert len(r["result"]["packageSha256"])==64
