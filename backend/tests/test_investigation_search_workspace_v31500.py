from pydantic import ValidationError
from app.investigation_search_workspace import SavedSearchRequest, SearchExecutionRequest, SearchCollectionRequest, profile
from app.client_contracts import TYPED_ENDPOINTS
from app.main import app

def test_saved_search_requires_query():
    x=SavedSearchRequest(schema="sc-workspace-investigative-saved-search-request/1.0",name="FOIA",query="contract invoice")
    assert x.query=="contract invoice"

def test_execution_requires_nonempty_query():
    try: SearchExecutionRequest(schema="sc-workspace-investigative-search-execution-request/1.0",query="")
    except ValidationError: pass
    else: raise AssertionError("expected query validation")

def test_collection_accepts_reference_objects():
    x=SearchCollectionRequest(schema="sc-workspace-investigative-search-collection-request/1.0",name="review set",objectRefs=[{"kind":"source","objectId":"s1"}])
    assert len(x.objectRefs)==1

def test_v315_typed_endpoints():
    expected={"investigativeSearchWorkspace","savedSearchStore","savedSearches","savedSearch","savedSearchRevisions","investigativeSearchExecute","investigativeSearchExecutions","investigativeSearchExecution","projectInvestigativeSearch","crossCaseInvestigativeSearch","investigativeSearchFacets","investigativeSearchDiagnostics","investigativeSearchSnapshotCreate","investigativeSearchSnapshots","investigativeSearchCollectionCreate","investigativeSearchCollections","investigativeSearchCollection","investigativeSearchDiscoveryGraph"}
    assert expected<=set(TYPED_ENDPOINTS); assert len(TYPED_ENDPOINTS)>=218

def test_openapi_search_routes():
    paths=app.openapi()["paths"]; assert "/v1/investigative-search-workspace" in paths; assert "/v1/investigative-search-workspace/cross-case/search" in paths; assert "/v1/investigative-search-workspace/projects/{project_id}/discovery-graph" in paths

def test_search_safety_boundaries():
    p=profile(); assert p["automaticEvidenceRanking"] is False; assert p["automaticSourceReliabilityScoring"] is False; assert p["automaticTruthDetermination"] is False; assert p["automaticRelationshipInference"] is False; assert p["rankingSemantics"].startswith("lexical-relevance")
