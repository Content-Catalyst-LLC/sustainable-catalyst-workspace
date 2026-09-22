import pytest
from pydantic import ValidationError

from app.client_contracts import TYPED_ENDPOINTS, profile as client_profile
from app.config import get_settings
from app.investigation_entity_workspace import (
    InvestigationEntityContextLinkRequest,
    InvestigationEntityMatchCandidateRequest,
    InvestigationEntityRelationshipRequest,
    ENTITY_WORKSPACE_SCHEMA,
    profile,
)
from app.main import app


def test_profile_human_control_boundaries():
    p=profile()
    assert p["workspaceVersion"]=="3.10.0"
    assert p["schema"]==ENTITY_WORKSPACE_SCHEMA
    assert p["automaticEntityMerge"] is False
    assert p["automaticIdentityConfirmation"] is False
    assert p["automaticRelationshipInference"] is False
    assert p["automaticCulpabilityInference"] is False
    assert p["automaticTruthDetermination"] is False
    assert p["automaticEvidenceRanking"] is False


def test_entity_typed_operations_and_openapi():
    expected={
        "entityResolutionWorkspace","entityStore","entities","entity","entityRevisions","entityAliasCreate","entityAliases",
        "entityIdentifierCreate","entityIdentifiers","entityRelationshipCreate","entityRelationships","entityContextLinkCreate","entityContextLinks",
        "entityMatchCandidateCreate","entityMatchCandidates","entityMatchCandidateReview","entityResolutionGraph","entityResolutionDiagnostics",
        "entityResolutionSnapshotCreate","entityResolutionSnapshots",
    }
    assert expected <= set(TYPED_ENDPOINTS)
    paths=app.openapi()["paths"]
    for name in expected:
        ep=TYPED_ENDPOINTS[name]
        assert ep["path"] in paths
        assert ep["method"].lower() in paths[ep["path"]]
    cp=client_profile(app.openapi())
    assert cp["workspaceVersion"]=="3.10.0"
    assert not cp["missingOpenApiOperations"]


def test_no_self_relationship_or_self_candidate():
    with pytest.raises(ValidationError):
        InvestigationEntityRelationshipRequest(schema="sc-workspace-investigation-entity-relationship-request/1.0",projectId="p",fromEntityId="e1",toEntityId="e1",relation="same-as")
    with pytest.raises(ValidationError):
        InvestigationEntityMatchCandidateRequest(schema="sc-workspace-investigation-entity-match-candidate-request/1.0",projectId="p",leftEntityId="e1",rightEntityId="e1")


def test_external_context_requires_fingerprint():
    with pytest.raises(ValidationError):
        InvestigationEntityContextLinkRequest(schema="sc-workspace-investigation-entity-context-link-request/1.0",projectId="p",entityId="e1",targetKind="document-ref",targetRef="doc:x",relation="mentioned-in")


def test_release_lineage():
    assert get_settings().service_version=="3.10.0"
