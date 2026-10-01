from app.reproducible_computational_linguistics_runtime import (
    ReproducibleComputationalLinguisticsRequest,
    execute,
    operation_catalog,
    profile,
)

def request(operation):
    return ReproducibleComputationalLinguisticsRequest.model_validate({
        "operation": operation,
        "studyId": "study-1",
        "corpusItems": [{
            "itemId": "doc-1",
            "text": "Original language evidence.",
            "languageIdentityId": "eng",
            "scriptIdentityId": "Latn",
            "sourceRefs": ["source:1"],
            "transformationLineage": [],
        }],
        "pipelineId": "pipe-1",
        "pipelineSteps": [{
            "stepId": "step-1",
            "operation": "tokenize",
            "parameters": {"mode": "bounded"},
            "inputRefs": ["doc-1"],
            "outputRefs": ["tokens-1"],
            "runtimeRef": "python:3.12",
        }],
        "runs": [{
            "runId": "run-1",
            "pipelineId": "pipe-1",
            "corpusSnapshotId": "snapshot-1",
            "runtimeIdentity": "python:3.12",
            "dependencyLockRef": "sha256:lock",
            "randomSeed": 7,
            "status": "recorded",
            "outputRefs": ["result-1"],
        }],
        "bindings": [{
            "bindingId": "binding-1",
            "runId": "run-1",
            "resultRef": "result-1",
            "sourceRefs": ["source:1"],
            "interpretation": "Human-reviewed interpretation.",
            "humanReviewed": True,
        }],
    })

def test_profile_guardrails():
    p=profile()
    assert p["version"]=="3.53.0"
    assert p["boundedOperationCount"]==7
    assert p["arbitraryCodeExecution"] is False
    assert p["automaticReproductionExecution"] is False

def test_operation_catalog_is_bounded():
    rows=operation_catalog()
    assert len(rows)==7
    assert all(x["bounded"] for x in rows)

def test_corpus_snapshot():
    r=execute(request("workspace.linguistics.corpus-snapshot"))
    assert r["result"]["itemCount"]==1
    assert r["result"]["originalLanguageFirst"] is True

def test_reproducibility_verify():
    r=execute(request("workspace.linguistics.reproducibility-verify"))
    assert r["result"]["verifiedRunCount"]==1
    assert r["result"]["automaticReproductionExecution"] is False

def test_package_lineage():
    r=execute(request("workspace.linguistics.reproducibility-package-lineage"))
    assert len(r["result"]["packageSha256"])==64
    assert r["result"]["provenancePreserved"] is True
