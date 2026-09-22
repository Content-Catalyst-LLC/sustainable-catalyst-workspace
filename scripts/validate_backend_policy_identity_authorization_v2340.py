#!/usr/bin/env python3
from pathlib import Path
from app.main import app, health
from app.client_contracts import profile as client_profile
from app.authorization import profile as auth_profile, ACTIONS
ROOT=Path(__file__).resolve().parents[1]

def main():
    h=health()
    assert h['version']=='2.34.0'
    assert h['backendPolicyIdentityAuthorizationConsolidation'] is True
    assert h['serverResolvedPrincipalIdentity'] is True
    assert h['routePolicyEnforcement'] is True
    assert h['authorizationDecisionReceipts'] is True
    p=auth_profile()
    assert p['backendAuthoritative'] is True
    assert p['browserAuthoritativeAuthorization'] is False
    assert p['defaultEffect']=='deny'
    assert p['clientSuppliedRolesTrusted'] is False
    assert p['clientSuppliedScopesTrusted'] is False
    assert len(ACTIONS)==8
    c=client_profile(app.openapi())
    assert c['workspaceVersion']=='2.34.0'
    assert c['typedEndpointCount']==34
    assert c['missingOpenApiOperations']==[]
    assert c['typedEndpoints']['authorizationProfile']['path']=='/v1/authorization'
    assert c['typedEndpoints']['authorizationEvaluate']['path']=='/v1/authorization/evaluate'
    assert (ROOT/'backend/migrations/031_backend_policy_identity_authorization_consolidation.sql').exists()
    php=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
    assert '/backend/authorization/evaluate' in php
    assert 'sc-workspace-typed-client-v2340.js' in php
    print('PASS: v2.34.0 backend policy, identity & authorization consolidation contract')
if __name__=='__main__': main()
