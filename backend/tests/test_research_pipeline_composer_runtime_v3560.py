from app.research_pipeline_composer_runtime import ResearchPipelineComposerRequest, execute, operation_catalog, profile

def req(operation):
    return ResearchPipelineComposerRequest.model_validate({
        "operation":operation,
        "pipelineId":"pipeline-1",
        "title":"Research pipeline",
        "sourceRefs":["source:1"],
        "steps":[
            {"stepId":"collect","operation":"workspace.collect","runtimeRef":"runtime:library","outputRefs":["artifact:1"]},
            {"stepId":"analyze","operation":"workspace.analyze","runtimeRef":"runtime:python","dependsOn":["collect"],"inputRefs":["artifact:1"],"outputRefs":["artifact:2"],"humanReviewRequired":True},
            {"stepId":"publish","operation":"workspace.publish","runtimeRef":"runtime:publication","dependsOn":["analyze"],"inputRefs":["artifact:2"]},
        ],
        "handoffs":[
            {"handoffId":"h1","fromStepId":"collect","toStepId":"analyze","artifactRefs":["artifact:1"],"contractRef":"contract:1","provenanceRefs":["prov:1"]},
            {"handoffId":"h2","fromStepId":"analyze","toStepId":"publish","artifactRefs":["artifact:2"],"contractRef":"contract:2","provenanceRefs":["prov:2"]},
        ],
    })

def test_profile():
    p=profile()
    assert p["version"]=="3.56.0"
    assert p["boundedOperationCount"]==7
    assert p["automaticExecutionEnabled"] is False
    assert p["arbitraryCodeExecution"] is False

def test_catalog():
    rows=operation_catalog()
    assert len(rows)==7
    assert all(x["bounded"] for x in rows)

def test_dependency_plan():
    r=execute(req("workspace.pipeline.dependency-plan"))
    assert r["result"]["orderedStepIds"]==["collect","analyze","publish"]
    assert r["result"]["ready"] is True

def test_readiness():
    r=execute(req("workspace.pipeline.readiness-check"))
    assert r["result"]["ready"] is True
    assert r["result"]["humanReviewRequiredStepCount"]==1

def test_package():
    r=execute(req("workspace.pipeline.reproducibility-package"))
    assert r["result"]["ready"] is True
    assert len(r["result"]["packageSha256"])==64
