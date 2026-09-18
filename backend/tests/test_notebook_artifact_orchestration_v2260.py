import pytest
from fastapi import HTTPException
from app.notebook_orchestration import EXECUTION_SCHEMA, compile_plan, profile
from app.schemas import NotebookExecutionPlanRequest, NotebookExecutionDispatchRequest


def test_profile_is_backend_authoritative_and_bounded():
    p=profile()
    assert p["backendAuthoritative"] is True
    assert p["browserSchedulesDependencies"] is False
    assert p["artifactSha256Pinning"] is True
    assert p["dependencyAwareDispatch"] is True
    assert p["arbitraryCodeExecution"] is False


def test_compile_plan_topologically_orders_explicit_cells():
    notebook={"schema":"sc-workspace-notebook/3.0","cells":[
        {"id":"b","execution":{"schema":EXECUTION_SCHEMA,"operation":"workspace.echo","dependsOnCellIds":["a"],"payload":{"n":2}}},
        {"id":"a","execution":{"schema":EXECUTION_SCHEMA,"operation":"workspace.echo","payload":{"n":1}}},
    ]}
    plan=compile_plan(notebook)
    assert plan["order"]==["a","b"]
    assert [x["stepId"] for x in plan["steps"]]==["a","b"]
    assert plan["edges"]==[{"from":"a","to":"b"}]


def test_compile_plan_rejects_cycles():
    notebook={"cells":[
        {"id":"a","execution":{"operation":"workspace.echo","dependsOnCellIds":["b"]}},
        {"id":"b","execution":{"operation":"workspace.echo","dependsOnCellIds":["a"]}},
    ]}
    with pytest.raises(HTTPException) as exc: compile_plan(notebook)
    assert exc.value.status_code==400
    assert exc.value.detail["code"]=="notebook-dependency-cycle"


def test_compile_plan_rejects_arbitrary_workspace_operation():
    notebook={"cells":[{"id":"a","execution":{"operation":"python.eval","payload":{"code":"1+1"}}}]}
    with pytest.raises(HTTPException) as exc: compile_plan(notebook)
    assert exc.value.detail["code"]=="unsupported-notebook-operation"


def test_compile_plan_selected_cells_must_be_executable():
    notebook={"cells":[{"id":"a"},{"id":"b","execution":{"operation":"workspace.echo"}}]}
    with pytest.raises(HTTPException) as exc: compile_plan(notebook,["a"])
    assert exc.value.detail["code"]=="selected-cells-not-executable"


def test_plan_and_dispatch_request_contracts():
    p=NotebookExecutionPlanRequest.model_validate({"schema":"sc-workspace-notebook-execution-plan-request/1.0","notebookId":"n1","expectedNotebookRevision":2})
    d=NotebookExecutionDispatchRequest.model_validate({"schema":"sc-workspace-notebook-execution-dispatch-request/1.0","idempotencyKey":"x"})
    assert p.notebookId=="n1" and p.expectedNotebookRevision==2
    assert d.idempotencyKey=="x"
