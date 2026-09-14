from types import SimpleNamespace

from app.compliance import evaluate_verification


def attestation(**kw):
    base=dict(attestation_id="a1", fingerprint="f"*64, source="specialist-runtime", classification="compliant", execution_succeeded=True, budget_compliant=True, sandbox_compliant=True,
              sandbox_attestation_json={"mode":"metadata-gate","attestedBy":"trusted-runtime","evidenceDigest":"a"*64}, checks_json=[])
    base.update(kw); return SimpleNamespace(**base)


def policy(**kw):
    base=dict(downstream_scopes_json=["publication","artifact-export"], allowed_sources_json=["specialist-runtime"], allowed_attestors_json=["trusted-runtime"], require_evidence_digest=True,
              allowed_sandbox_modes_json=["metadata-gate"], accepted_classifications_json=["compliant"], require_budget_compliant=True, require_sandbox_compliant=True)
    base.update(kw); return SimpleNamespace(**base)


def waiver(checks,scope="publication"):
    return SimpleNamespace(waiver_id="w1",attestation_id="a1",human_authorized=True,downstream_scopes_json=[scope],expires_at=None,waived_checks_json=checks)


def test_verified_compliant_attestation():
    out=evaluate_verification(attestation(),policy(),"publication")
    assert out["eligible"] is True and out["classification"]=="verified"


def test_reject_untrusted_attestor():
    a=attestation(sandbox_attestation_json={"mode":"metadata-gate","attestedBy":"unknown","evidenceDigest":"a"*64})
    out=evaluate_verification(a,policy(),"publication")
    assert out["eligible"] is False and any(x["check"]=="attestor-trusted" and x["status"]=="fail" for x in out["checks"])


def test_scoped_human_waiver_can_cover_sandbox_deviation_without_rewriting_attestation():
    a=attestation(classification="sandbox-deviation",sandbox_compliant=False,checks_json=[{"check":"sandbox-networkMode","status":"fail"}])
    out=evaluate_verification(a,policy(),"publication",waiver(["sandbox-networkMode"]))
    assert out["eligible"] is True and out["classification"]=="verified-with-waiver"
    assert a.classification=="sandbox-deviation"


def test_waiver_cannot_cover_failed_execution():
    a=attestation(classification="execution-failed",execution_succeeded=False,checks_json=[{"check":"job-succeeded","status":"fail"}])
    out=evaluate_verification(a,policy(),"publication",waiver(["job-succeeded"]))
    assert out["eligible"] is False and out["classification"]=="rejected"


def test_incomplete_is_never_verified_with_waiver():
    a=attestation(classification="incomplete",budget_compliant=False,checks_json=[{"check":"budget-cpuCoreSeconds","status":"unknown"}])
    out=evaluate_verification(a,policy(),"publication")
    assert out["eligible"] is False and out["classification"]=="incomplete"


def test_routes_and_contracts_present():
    from pathlib import Path
    r=Path(__file__).resolve().parents[1]
    main=(r/'backend/app/main.py').read_text(); wp=(r/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
    assert '/v1/runtime-trust-policies' in main and '/v1/compliance-waivers' in main and '/v1/attestation-verifications' in main
    assert 'backend-attestation-verifications' in wp


def test_migration_grants_new_tables():
    from pathlib import Path
    sql=(Path(__file__).resolve().parents[1]/'backend/migrations/010_attestation_verification_compliance_runtime_trust.sql').read_text()
    for token in ['workspace_runtime_trust_policy_heads','workspace_compliance_waivers','workspace_attestation_verification_receipts','TO sc_workspace']:
        assert token in sql


def test_release_lineage_is_v290():
    from pathlib import Path
    r=Path(__file__).resolve().parents[1]
    for p in ['wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php','wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-production-certification.php']:
        t=(r/p).read_text(); assert "const PREVIOUS_RELEASE = '2.9.0';" in t; assert "const ROLLBACK_RELEASE = '2.9.0';" in t
