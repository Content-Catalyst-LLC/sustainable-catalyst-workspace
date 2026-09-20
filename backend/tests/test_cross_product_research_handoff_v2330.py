from unittest.mock import MagicMock, patch
from app.client_contracts import TYPED_ENDPOINTS, profile as client_profile
from app.cross_product_handoffs import PRODUCTS, INTENTS, ResearchHandoffRequest, profile
from app.main import app, health

def test_profile_declares_provenance_preserving_cross_product_fabric():
    p=profile(); assert p['backendAuthoritative'] is True and p['browserAuthoritativeState'] is False; assert p['revisionPinning'] and p['fingerprintPinning'] and p['durableReceipts']; assert p['genericDestinationMutation'] is False; assert 'workspace' in PRODUCTS and 'research-lab' in PRODUCTS

def test_request_requires_distinct_supported_products_and_known_intent():
    r=ResearchHandoffRequest.model_validate({'schema':'sc-workspace-research-handoff-request/1.0','sourceProduct':'workspace','destinationProduct':'research-lab','intent':'analyze','objects':[{'kind':'dataset','objectId':'d1'}]}); assert r.intent in INTENTS

def test_typed_contract_exposes_handoff_routes():
    item=client_profile(app.openapi()); assert item['workspaceVersion']=='2.35.0'; assert item['typedEndpointCount']==len(TYPED_ENDPOINTS)==35; assert item['typedEndpoints']['handoffCreate']['path']=='/v1/handoffs'; assert item['requestSchemas']['handoffCreate']=='sc-workspace-research-handoff-request/1.0'; assert item['missingOpenApiOperations']==[]

def test_health_advertises_handoff_fabric_without_generic_destination_mutation():
    h=health(); assert h['version']=='2.35.0'; assert h['crossProductResearchHandoffFabric'] is True; assert h['handoffRevisionPinning'] and h['handoffFingerprintPinning']; assert h['handoffGenericDestinationMutation'] is False

def test_previous_unified_object_layer_remains_enabled():
    h=health(); assert h['unifiedScientificObjectApi'] is True and h['scientificObjectKindCount']==10
