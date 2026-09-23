from pydantic import ValidationError
from app.investigation_media_workspace import (InvestigationMediaArtifactRequest, InvestigationMediaLocatorRequest,
    InvestigationMediaDerivativeRequest, InvestigationMediaRelationRequest, profile)
from app.client_contracts import TYPED_ENDPOINTS
from app.main import app

def test_media_artifact_contract():
    p=InvestigationMediaArtifactRequest(schema="sc-workspace-investigation-media-artifact-request/1.0",projectId="p",mediaType="video",title="clip",sourceRef="library:clip",sourceFingerprint="12345678",contentHash="abcdef123456")
    assert p.mediaType=="video" and p.contentHashAlgorithm=="sha256"

def test_locator_requires_payload_unless_whole_artifact():
    try:
        InvestigationMediaLocatorRequest(schema="sc-workspace-investigation-media-locator-request/1.0",projectId="p",artifactId="a",locatorType="frame")
    except ValidationError: pass
    else: raise AssertionError("expected locator validation error")
    x=InvestigationMediaLocatorRequest(schema="sc-workspace-investigation-media-locator-request/1.0",projectId="p",artifactId="a",locatorType="whole-artifact")
    assert x.locator=={}

def test_derivative_endpoints_must_differ():
    try:
        InvestigationMediaDerivativeRequest(schema="sc-workspace-investigation-media-derivative-request/1.0",projectId="p",parentArtifactId="a",childArtifactId="a",transformationType="clip")
    except ValidationError: pass
    else: raise AssertionError("expected derivative endpoint validation error")

def test_relation_endpoints_must_differ():
    try:
        InvestigationMediaRelationRequest(schema="sc-workspace-investigation-media-relation-request/1.0",projectId="p",fromArtifactId="a",toArtifactId="a",relation="related-to")
    except ValidationError: pass
    else: raise AssertionError("expected relation endpoint validation error")

def test_v313_typed_endpoints():
    expected={"mediaProvenanceWorkspace","mediaArtifactStore","mediaArtifacts","mediaArtifact","mediaArtifactRevisions","mediaLocatorCreate","mediaLocators","mediaDerivativeCreate","mediaDerivatives","mediaContextLinkCreate","mediaContextLinks","mediaRelationCreate","mediaRelations","mediaProvenanceGraph","mediaDiagnostics","mediaIntegrity","mediaSnapshotCreate","mediaSnapshots"}
    assert expected<=set(TYPED_ENDPOINTS); assert len(TYPED_ENDPOINTS)>=182

def test_openapi_and_safety_boundaries():
    paths=app.openapi()["paths"]; assert "/v1/media-provenance-workspace" in paths; assert "/v1/media-provenance-workspace/projects/{project_id}/integrity" in paths
    p=profile(); assert p["automaticMediaSimilarityMatching"] is False; assert p["automaticAuthenticityDetermination"] is False; assert p["automaticTruthDetermination"] is False; assert p["binaryMediaStorage"] is False
