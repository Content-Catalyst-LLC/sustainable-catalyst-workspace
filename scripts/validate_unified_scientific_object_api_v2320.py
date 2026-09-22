#!/usr/bin/env python3
from pathlib import Path
from app.client_contracts import TYPED_ENDPOINTS, profile as client_profile
from app.main import app, health
from app.scientific_objects import OBJECT_KINDS, REVISIONED_KINDS, profile
ROOT=Path(__file__).resolve().parents[1]

p=profile()
assert p['schema']=='sc-workspace-scientific-object-api/1.0'
assert p['backendAuthoritative'] is True and p['browserAuthoritativeState'] is False
assert len(OBJECT_KINDS)==10 and 'scientific-receipt' in OBJECT_KINDS
assert len(REVISIONED_KINDS)==7 and p['genericArbitraryMutationEndpoint'] is False
c=client_profile(app.openapi())
assert c['workspaceVersion']=='2.32.0' and c['typedEndpointCount']==len(TYPED_ENDPOINTS)==25
assert c['missingOpenApiOperations']==[]
h=health(); assert h['version']=='2.32.0' and h['unifiedScientificObjectApi'] is True and h['scientificObjectKindCount']==10
wp=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
main=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.32.0.js').read_text()
typed=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-typed-client-v2320.js').read_text()
assert 'backend_typed_scientific_object_relations' in wp and 'SCWorkspaceScientificObjectBoundary' in main and 'SCWorkspaceScientificObjects' in typed
print('PASS: v2.32.0 unified scientific object API contract')
