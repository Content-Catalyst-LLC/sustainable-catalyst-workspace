from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.registry import RUN_TRANSITIONS, dataset_metadata, model_metadata, parameter_set_metadata
from app.schemas import (
    DatasetStoreRequest,
    ExecutionEnvironmentStoreRequest,
    ExecutionRunCreateRequest,
    ExecutionRunOutputRequest,
    JobCreateRequest,
    ModelStoreRequest,
    ParameterSetStoreRequest,
)


def test_dataset_registry_schema_accepts_revision_precondition():
    payload = DatasetStoreRequest.model_validate({
        "schema": "sc-workspace-dataset-record/1.0",
        "datasetId": "dataset-energy-demand",
        "name": "Energy demand",
        "datasetType": "timeseries",
        "sourceKind": "external",
        "externalUri": "https://example.test/demand.csv",
        "expectedRevision": 0,
    })
    assert payload.datasetType == "timeseries"
    assert payload.expectedRevision == 0


def test_model_registry_schema_carries_execution_descriptor_not_arbitrary_url():
    payload = ModelStoreRequest.model_validate({
        "schema": "sc-workspace-model-record/1.0",
        "modelId": "model-demand-forecast",
        "name": "Demand forecast",
        "modelKind": "forecasting",
        "executionTarget": "lab",
        "executionOperation": "forecast.run",
    })
    assert payload.executionTarget == "lab"
    assert not hasattr(payload, "targetUrl")


def test_parameter_set_can_bind_model():
    payload = ParameterSetStoreRequest.model_validate({
        "schema": "sc-workspace-parameter-set/1.0",
        "parameterSetId": "params-base",
        "modelId": "model-demand-forecast",
        "name": "Base case",
        "parameters": {"horizon": 12},
    })
    assert payload.parameters["horizon"] == 12


def test_execution_run_accepts_revision_pinned_refs():
    payload = ExecutionRunCreateRequest.model_validate({
        "schema": "sc-workspace-execution-run/1.0",
        "runId": "run-1",
        "datasetRefs": [{"datasetId": "dataset-energy-demand", "revision": 2}],
        "modelRef": {"modelId": "model-demand-forecast", "revision": 3},
        "parameterSetRef": {"parameterSetId": "params-base", "revision": 1},
        "targetProduct": "lab",
        "operation": "forecast.run",
    })
    assert payload.datasetRefs[0].revision == 2
    assert payload.modelRef.revision == 3


def test_job_request_can_link_execution_run():
    payload = JobCreateRequest.model_validate({
        "schema": "sc-workspace-job-request/1.0",
        "targetProduct": "workspace",
        "operation": "workspace.echo",
        "executionRunId": "run-1",
    })
    assert payload.executionRunId == "run-1"


def test_run_output_requires_valid_sha_shape_when_provided():
    with pytest.raises(ValidationError):
        ExecutionRunOutputRequest.model_validate({
            "schema": "sc-workspace-execution-run-output/1.0",
            "outputId": "forecast",
            "sha256": "not-a-digest",
        })


def test_terminal_success_is_immutable_but_failed_runs_can_requeue():
    assert RUN_TRANSITIONS["succeeded"] == {"succeeded"}
    assert "queued" in RUN_TRANSITIONS["failed"]


def test_execution_environment_schema_captures_manifests_without_secret_values():
    payload = ExecutionEnvironmentStoreRequest.model_validate({
        "schema": "sc-workspace-execution-environment/1.0",
        "environmentId": "env-py312",
        "name": "Python 3.12 analysis",
        "runtime": {"language": "python", "version": "3.12"},
        "dependencies": {"manager": "pip", "requirementsSha256": "a" * 64},
        "container": {"image": "python:3.12-slim", "digest": "sha256:example"},
        "randomSeeds": {"python": 42},
        "environmentVariableNames": ["OMP_NUM_THREADS", "API_TOKEN"],
    })
    assert payload.runtime["version"] == "3.12"
    assert not hasattr(payload, "environmentVariableValues")


def test_execution_run_accepts_revision_pinned_environment_ref():
    payload = ExecutionRunCreateRequest.model_validate({
        "schema": "sc-workspace-execution-run/1.0",
        "operation": "workspace.echo",
        "environmentRef": {"environmentId": "env-py312", "revision": 2},
    })
    assert payload.environmentRef.environmentId == "env-py312"
    assert payload.environmentRef.revision == 2
