from pydantic import ValidationError
from app.investigation_source_integrity_workspace import InvestigationSourceRequest, SourceCustodyEventRequest, IntegrityAssertionRequest, profile
from app.client_contracts import TYPED_ENDPOINTS
from app.main import app

def test_source_contract_requires_fingerprint():
    x=InvestigationSourceRequest(schema="sc-workspace-investigation-source-request/1.0",projectId="p",sourceType="public-record",title="record",sourceRef="library:record",contentFingerprint="12345678")
    assert x.sourceType=="public-record"

def test_source_fingerprint_minimum():
    try: InvestigationSourceRequest(schema="sc-workspace-investigation-source-request/1.0",projectId="p",sourceType="document",title="d",sourceRef="x",contentFingerprint="123")
    except ValidationError: pass
    else: raise AssertionError("expected content fingerprint validation")

def test_custody_requires_custodian():
    try: SourceCustodyEventRequest(schema="sc-workspace-source-custody-event-request/1.0",projectId="p",sourceId="s",action="received",custodianRef="")
    except ValidationError: pass
    else: raise AssertionError("expected custodian validation")

def test_integrity_assertion_is_explicit_status():
    x=IntegrityAssertionRequest(schema="sc-workspace-integrity-assertion-request/1.0",projectId="p",sourceId="s",assertionType="hash-match",status="verified")
    assert x.status=="verified"

def test_v314_typed_endpoints():
    expected={"sourceIntegrityWorkspace","sourceStore","sources","source","sourceRevisions","sourceProvenanceEventCreate","sourceProvenanceEvents","sourceCustodyEventCreate","sourceCustodyEvents","integrityAssertionCreate","integrityAssertions","sourceEvidenceBindingCreate","sourceEvidenceBindings","sourceIntegrityGraph","sourceIntegrityDiagnostics","sourceIntegrityAssessment","sourceIntegritySnapshotCreate","sourceIntegritySnapshots"}
    assert expected<=set(TYPED_ENDPOINTS); assert len(TYPED_ENDPOINTS)>=200

def test_openapi_and_safety_boundaries():
    paths=app.openapi()["paths"]; assert "/v1/source-integrity-workspace" in paths; assert "/v1/source-integrity-workspace/projects/{project_id}/integrity" in paths
    p=profile(); assert p["automaticSourceReliabilityScoring"] is False; assert p["automaticAuthenticityDetermination"] is False; assert p["automaticEvidenceRanking"] is False; assert p["automaticTruthDetermination"] is False
