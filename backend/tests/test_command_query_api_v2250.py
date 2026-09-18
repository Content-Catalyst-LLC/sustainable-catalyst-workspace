from types import SimpleNamespace
from app.command_query import COMMANDS, QUERIES, profile
from app.schemas import CommandExecuteRequest, QueryExecuteRequest

def test_profile_declares_server_command_query_boundary():
    p=profile()
    assert p["mode"]=="server-command-query"
    assert p["backendAuthoritative"] is True
    assert p["browserCommandAuthority"] is False
    assert p["queriesMutate"] is False
    assert p["readModelsGeneratedServerSide"] is True
    assert p["commandCount"]==9 and p["queryCount"]==9
    assert p["arbitraryCodeExecution"] is False

def test_command_registry_is_bounded():
    assert COMMANDS == ("project.put","project.delete","notebook.put","notebook.delete","artifact.put","artifact.delete","job.submit","job.cancel","job.retry")

def test_query_registry_is_bounded_and_read_only():
    assert "workspace.overview" in QUERIES and "project.detail" in QUERIES and "provenance.receipts" in QUERIES

def test_command_request_contract():
    x=CommandExecuteRequest.model_validate({"schema":"sc-workspace-command-request/1.0","command":"project.delete","idempotencyKey":"abc","payload":{"projectId":"p1"}})
    assert x.command=="project.delete" and x.idempotencyKey=="abc"

def test_query_request_contract():
    x=QueryExecuteRequest.model_validate({"schema":"sc-workspace-query-request/1.0","query":"workspace.overview","parameters":{}})
    assert x.query=="workspace.overview"
