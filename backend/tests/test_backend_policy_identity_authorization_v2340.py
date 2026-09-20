from app.authorization import (
    ACTIONS,
    POLICY_ID,
    AuthorizationEvaluateRequest,
    action_for_request,
    evaluate,
    principal_payload,
    profile,
)
from app.client_contracts import TYPED_ENDPOINTS, profile as client_profile
from app.main import app, health
from app.security import ServiceIdentity


def identity():
    return ServiceIdentity(
        user_key="42",
        principal_id="wp-user:42",
        principal_type="wordpress-user",
        service_principal="wordpress-proxy",
        authentication_method="service-bearer+wordpress-user-context",
    )


def test_profile_is_backend_authoritative_default_deny_and_server_resolved():
    p = profile()
    assert p["backendAuthoritative"] is True
    assert p["browserAuthoritativeAuthorization"] is False
    assert p["defaultEffect"] == "deny"
    assert p["routePolicyEnforcement"] is True
    assert p["clientSuppliedRolesTrusted"] is False
    assert p["clientSuppliedScopesTrusted"] is False
    assert p["durableDecisionReceipts"] is True


def test_principal_identity_is_server_resolved_and_user_scoped():
    p = principal_payload(identity())
    assert p["principalId"] == "wp-user:42"
    assert p["servicePrincipal"] == "wordpress-proxy"
    assert p["policyId"] == POLICY_ID
    assert p["serverResolved"] is True
    assert set(ACTIONS).issubset(set(p["effectiveScopes"]))


def test_route_policy_maps_sensitive_flows_to_specific_actions():
    assert action_for_request("POST", "/v1/commands/execute") == "workspace.execute"
    assert action_for_request("POST", "/v1/sync/envelopes") == "workspace.sync"
    assert action_for_request("POST", "/v1/handoffs") == "workspace.handoff.prepare"
    assert action_for_request("POST", "/v1/handoffs/h1/accept") == "workspace.handoff.accept"
    assert action_for_request("GET", "/v1/scientific-objects") == "workspace.read"


def test_authorization_decision_is_deterministic_and_unknown_actions_deny():
    i = identity()
    allow = evaluate(i, "workspace.read", "workspace")
    again = evaluate(i, "workspace.read", "workspace")
    deny = evaluate(i, "workspace.superuser", "workspace")
    assert allow["effect"] == "allow"
    assert allow["decisionFingerprint"] == again["decisionFingerprint"]
    assert len(allow["decisionFingerprint"]) == 64
    assert deny["effect"] == "deny" and deny["reason"] == "unknown-action"


def test_v234_health_and_typed_contract_expose_consolidated_authorization():
    h = health()
    assert h["version"] == "2.35.0"
    assert h["backendPolicyIdentityAuthorizationConsolidation"] is True
    assert h["serverResolvedPrincipalIdentity"] is True
    assert h["authorizationDecisionReceipts"] is True
    c = client_profile(app.openapi())
    assert c["workspaceVersion"] == "2.35.0"
    assert c["typedEndpointCount"] == len(TYPED_ENDPOINTS) == 35
    assert c["typedEndpoints"]["authorizationEvaluate"]["path"] == "/v1/authorization/evaluate"
    assert c["requestSchemas"]["authorizationEvaluate"] == "sc-workspace-authorization-evaluate-request/1.0"
    assert c["missingOpenApiOperations"] == []
    AuthorizationEvaluateRequest.model_validate({
        "schema":"sc-workspace-authorization-evaluate-request/1.0",
        "action":"workspace.read",
        "resourceKind":"workspace",
    })
