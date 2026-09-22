import pytest
from pydantic import ValidationError

from app.client_contracts import TYPED_ENDPOINTS, profile as client_profile
from app.config import get_settings
from app.investigation_documentary_workspace import (
    DOCUMENTARY_WORKSPACE_SCHEMA,
    InvestigationDocumentaryContextLinkRequest,
    InvestigationTestimonyRelationRequest,
    InvestigationTestimonyRequest,
    profile,
)
from app.main import app


def test_profile_human_control_boundaries():
    p = profile()
    assert p["workspaceVersion"] == "3.11.0"
    assert p["schema"] == DOCUMENTARY_WORKSPACE_SCHEMA
    assert p["automaticCredibilityScoring"] is False
    assert p["automaticTruthDetermination"] is False
    assert p["automaticEvidenceRanking"] is False
    assert p["automaticCulpabilityInference"] is False
    assert p["automaticMotiveInference"] is False
    assert p["automaticNarrativeSelection"] is False


def test_documentary_typed_operations_and_openapi():
    expected = {
        "documentaryEvidenceWorkspace","documentStore","documents","document","documentRevisions",
        "documentExcerptCreate","documentExcerpts","testimonyStore","testimonies","testimony","testimonyRevisions",
        "documentaryContextLinkCreate","documentaryContextLinks","testimonyRelationCreate","testimonyRelations",
        "documentaryGraph","documentaryAnalysis","documentarySnapshotCreate","documentarySnapshots",
    }
    assert expected <= set(TYPED_ENDPOINTS)
    paths = app.openapi()["paths"]
    for name in expected:
        ep = TYPED_ENDPOINTS[name]
        assert ep["path"] in paths
        assert ep["method"].lower() in paths[ep["path"]]
    cp = client_profile(app.openapi())
    assert cp["workspaceVersion"] == "3.11.0"
    assert not cp["missingOpenApiOperations"]
    assert len(TYPED_ENDPOINTS) >= 150


def test_testimony_requires_source_provenance():
    with pytest.raises(ValidationError):
        InvestigationTestimonyRequest(
            schema="sc-workspace-investigation-testimony-request/1.0",
            projectId="p", testimonyType="interview", title="Interview", text="Statement",
        )


def test_testimony_relation_rejects_self_relation():
    with pytest.raises(ValidationError):
        InvestigationTestimonyRelationRequest(
            schema="sc-workspace-investigation-testimony-relation-request/1.0",
            projectId="p", fromTestimonyId="t1", toTestimonyId="t1", relation="corroborates",
        )


def test_external_documentary_context_requires_fingerprint():
    with pytest.raises(ValidationError):
        InvestigationDocumentaryContextLinkRequest(
            schema="sc-workspace-investigation-documentary-context-link-request/1.0",
            projectId="p", sourceKind="document", sourceId="d1",
            targetKind="evidence-ref", targetRef="evidence:x", relation="supports",
        )


def test_release_lineage():
    assert get_settings().service_version == "3.11.0"
