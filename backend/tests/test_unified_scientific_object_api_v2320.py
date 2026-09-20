from unittest.mock import MagicMock, patch

from app.client_contracts import TYPED_ENDPOINTS, profile as client_profile
from app.main import app, health
from app.scientific_objects import OBJECT_KINDS, REVISIONED_KINDS, list_objects, normalize, profile


def test_profile_declares_unified_backend_authoritative_object_layer():
    item = profile()
    assert item["schema"] == "sc-workspace-scientific-object-api/1.0"
    assert item["backendAuthoritative"] is True and item["browserAuthoritativeState"] is False
    assert item["canonicalStore"] == "postgresql"
    assert "dataset" in item["supportedKinds"] and "scientific-receipt" in item["supportedKinds"]
    assert set(item["revisionedKinds"]) == REVISIONED_KINDS
    assert item["genericArbitraryMutationEndpoint"] is False


def test_normalized_dataset_has_canonical_identity_revision_and_fingerprint():
    item = normalize("dataset", {"datasetId":"ds1","projectId":"p1","name":"Observations","revision":3,"fingerprint":"a"*64,"createdAt":"2026-01-01T00:00:00Z","updatedAt":"2026-01-02T00:00:00Z","datasetType":"table"})
    assert item["schema"] == "sc-workspace-scientific-object/1.0"
    assert item["kind"] == "dataset" and item["objectId"] == "ds1" and item["revision"] == 3
    assert item["fingerprint"] == "a"*64 and len(item["objectFingerprint"]) == 64
    assert item["capabilities"]["revisionHistory"] is True and item["capabilities"]["genericMutation"] is False


def test_unified_list_can_merge_multiple_kinds_and_project_filter():
    with patch("app.scientific_objects.list_datasets", return_value=[{"datasetId":"ds1","projectId":"p1","name":"D","revision":1,"fingerprint":"d"*64,"createdAt":"2026-01-01","updatedAt":"2026-01-02"}]), \
         patch("app.scientific_objects.list_models", return_value=[{"modelId":"m1","projectId":"p1","name":"M","revision":2,"fingerprint":"m"*64,"createdAt":"2026-01-01","updatedAt":"2026-01-03"}]):
        with patch("app.scientific_objects.OBJECT_KINDS", ("dataset","model")):
            items = list_objects(MagicMock(), "u1", project_id="p1", limit=10)
    assert [x["kind"] for x in items] == ["model", "dataset"]


def test_typed_contract_exposes_five_unified_scientific_object_routes():
    item = client_profile(app.openapi())
    assert item["workspaceVersion"] in {"2.32.0","2.34.0"}
    assert item["typedEndpointCount"] == len(TYPED_ENDPOINTS) and item["typedEndpointCount"] >= 25
    assert item["typedEndpoints"]["scientificObjects"]["path"] == "/v1/scientific-objects"
    assert item["typedEndpoints"]["scientificObjectGet"]["path"] == "/v1/scientific-objects/{kind}/{object_id}"
    assert item["typedEndpoints"]["scientificObjectRelations"]["path"].endswith("/relations")
    assert item["missingOpenApiOperations"] == []


def test_health_advertises_unified_scientific_object_api():
    item = health()
    assert item["version"] in {"2.32.0","2.34.0"}
    assert item["unifiedScientificObjectApi"] is True
    assert item["scientificObjectKindCount"] == len(OBJECT_KINDS)
    assert item["scientificObjectGenericMutation"] is False
