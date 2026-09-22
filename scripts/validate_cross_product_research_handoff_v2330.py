#!/usr/bin/env python3
from pathlib import Path
from app.main import app, health
from app.client_contracts import profile as client_profile
from app.cross_product_handoffs import profile as handoff_profile, PRODUCTS, INTENTS
ROOT=Path(__file__).resolve().parents[1]
def main():
 h=health(); assert h['version']=='2.34.0' and h['crossProductResearchHandoffFabric'] is True and h['handoffGenericDestinationMutation'] is False
 p=handoff_profile(); assert p['backendAuthoritative'] is True and p['revisionPinning'] and p['fingerprintPinning'] and p['durableReceipts']; assert len(PRODUCTS)>=9 and len(INTENTS)>=10
 c=client_profile(app.openapi()); assert c['workspaceVersion']=='2.34.0' and c['typedEndpointCount']==34 and c['missingOpenApiOperations']==[]
 assert c['typedEndpoints']['handoffCreate']['path']=='/v1/handoffs' and c['typedEndpoints']['handoffAccept']['path']=='/v1/handoffs/{handoff_id}/accept'
 assert (ROOT/'backend/migrations/030_cross_product_research_handoff_fabric.sql').exists()
 php=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); assert '/backend/handoffs/profile' in php and 'sc-workspace-typed-client-v2340.js' in php
 print('PASS: v2.34.0 cross-product research handoff fabric contract')
if __name__=='__main__': main()
