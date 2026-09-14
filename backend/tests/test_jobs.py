from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.routing import RouteBlocked, execute_job, route_registry
from app.schemas import JobCreateRequest


def test_job_request_accepts_workspace_task():
    payload = JobCreateRequest.model_validate({
        "schema": "sc-workspace-job-request/1.0",
        "jobType": "workspace-task",
        "targetProduct": "workspace",
        "operation": "workspace.echo",
        "payload": {"message": "hello"},
    })
    assert payload.targetProduct == "workspace"
    assert payload.operation == "workspace.echo"


def test_job_request_rejects_browser_supplied_target_url_shape():
    with pytest.raises(ValidationError):
        JobCreateRequest.model_validate({
            "schema": "sc-workspace-job-request/1.0",
            "targetProduct": "https://example.com",
            "operation": "run",
        })


def test_workspace_echo_executes_locally():
    row = SimpleNamespace(
        target_product="workspace",
        operation="workspace.echo",
        payload={"payload": {"value": 42}},
        user_key="wp:1",
        job_id="job-test",
        project_id="",
        request_fingerprint="0" * 64,
    )
    result = execute_job(None, row)
    assert result["echo"] == {"value": 42}


def test_unknown_workspace_operation_blocks_instead_of_guessing():
    row = SimpleNamespace(
        target_product="workspace",
        operation="workspace.unknown",
        payload={"payload": {}},
        user_key="wp:1",
        job_id="job-test",
        project_id="",
        request_fingerprint="0" * 64,
    )
    with pytest.raises(RouteBlocked):
        execute_job(None, row)


def test_route_registry_is_server_configured_only():
    registry = route_registry()
    assert registry["workspace"]["configured"] is True
    assert registry["workspace"]["serverConfiguredOnly"] is True
    for target in ["core", "lab", "workbench", "decision-studio", "library", "site-intelligence"]:
        assert target in registry
        assert registry[target]["serverConfiguredOnly"] is True
