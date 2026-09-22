import pytest
from pydantic import ValidationError

from app.client_contracts import TYPED_ENDPOINTS, REQUEST_SCHEMAS, profile as client_profile
from app.frontend_runtime import profile as frontend_profile
from app.investigative_research_workspace import (
    InvestigationEvidenceLinkRequest,
    InvestigationStatementRelationRequest,
    profile as investigative_profile,
)
from app.main import app
from app.production_certification import profile as certification_profile


def test_v370_investigative_profile_boundaries():
    item = investigative_profile()
    assert item["workspaceVersion"] == "3.7.0"
    assert item["referenceFirst"] is True
    assert item["statementRevisionHistory"] is True
    assert item["immutableEvidenceLinks"] is True
    assert item["visualResearchGraphOverlay"] is True
    assert item["automaticTruthDetermination"] is False
    assert item["automaticEvidenceRanking"] is False
    assert item["automaticClaimScoring"] is False


def test_v370_external_evidence_requires_fingerprint_and_self_relation_is_rejected():
    with pytest.raises(ValidationError):
        InvestigationEvidenceLinkRequest(
            schema="sc-workspace-investigation-evidence-link-request/1.0",
            projectId="p1", statementId="s1", evidenceRef="external:document:1",
            relation="supports",
        )
    with pytest.raises(ValidationError):
        InvestigationStatementRelationRequest(
            schema="sc-workspace-investigation-statement-relation-request/1.0",
            projectId="p1", fromStatementId="s1", toStatementId="s1", relation="contradicts",
        )


def test_v370_typed_contract_has_investigative_operations():
    item = client_profile(app.openapi())
    assert len(TYPED_ENDPOINTS) >= 82
    assert item["typedEndpointCount"] == len(TYPED_ENDPOINTS)
    assert not item["missingOpenApiOperations"]
    expected = {
        "investigativeResearchWorkspace", "investigationStatementStore", "investigationStatements",
        "investigationStatement", "investigationStatementRevisions", "investigationEvidenceLinkCreate",
        "investigationEvidenceLinks", "investigationStatementRelationCreate", "investigationStatementRelations",
        "investigativeResearchProject", "investigativeResearchSnapshotCreate", "investigativeResearchSnapshots",
    }
    assert expected.issubset(TYPED_ENDPOINTS)
    assert REQUEST_SCHEMAS["investigationStatementStore"] == "sc-workspace-investigation-statement-request/1.0"
    assert REQUEST_SCHEMAS["investigationEvidenceLinkCreate"] == "sc-workspace-investigation-evidence-link-request/1.0"


def test_v370_release_lineage_frontend_and_routes():
    cert = certification_profile()
    assert cert["workspaceVersion"] == "3.7.0"
    assert cert["migrationLineage"] == "038_claims_evidence_investigative_research_workspace.sql"
    assert cert["rollbackBaseline"] == "3.6.0"
    assert cert["certificationGates"]["claimsEvidenceInvestigativeResearchWorkspace"] == "release-gate"
    frontend = frontend_profile()
    assert frontend["workspaceVersion"] == "3.7.0"
    assert "v3.7.0" in frontend["activeShell"]
    paths = app.openapi()["paths"]
    expected = [
        "/v1/investigative-research-workspace",
        "/v1/investigative-research-workspace/statements",
        "/v1/investigative-research-workspace/statements/{statement_id}",
        "/v1/investigative-research-workspace/statements/{statement_id}/revisions",
        "/v1/investigative-research-workspace/evidence-links",
        "/v1/investigative-research-workspace/statement-relations",
        "/v1/investigative-research-workspace/projects/{project_id}",
        "/v1/investigative-research-workspace/projects/{project_id}/snapshots",
    ]
    for path in expected:
        assert path in paths
