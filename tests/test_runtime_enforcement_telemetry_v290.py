from types import SimpleNamespace

from app.schemas import RuntimeExecutionAttestationRequest
from app.telemetry import evaluate_runtime_attestation


def decision(**kw):
    base={
      "resource_budget_json":{"cpuCores":1.0,"memoryMb":512,"wallSeconds":60,"outputBytes":1048576,"pids":32,"tempStorageMb":128},
      "sandbox_json":{"mode":"adapter-attested","networkMode":"none","readOnlyRootFilesystem":True,"noNewPrivileges":True,"dropAllCapabilities":True,"allowHostFilesystem":False,"allowDockerSocket":False,"allowPrivileged":False,"requirePinnedContainer":True},
    }
    base.update(kw); return SimpleNamespace(**base)


def job(status="succeeded"):
    return SimpleNamespace(status=status)


def payload(**usage):
    observed={"cpuCoreSeconds":4.5,"peakMemoryMb":128,"wallSeconds":5.0,"outputBytes":1024,"pidsPeak":4,"tempStorageMbPeak":8}
    observed.update(usage)
    return RuntimeExecutionAttestationRequest.model_validate({
      "schema":"sc-workspace-runtime-execution-attestation/1.0","source":"specialist-runtime","observedUsage":observed,
      "sandboxAttestation":{"mode":"adapter-attested","networkMode":"none","readOnlyRootFilesystem":True,"noNewPrivileges":True,"dropAllCapabilities":True,"hostFilesystemAccess":False,"dockerSocketAccess":False,"privilegedExecution":False,"pinnedContainer":True,"attestedBy":"runtime-smoke","evidenceDigest":"a"*64}
    })


def test_compliant_runtime_attestation():
    out=evaluate_runtime_attestation(decision(),job(),payload())
    assert out["classification"]=="compliant"
    assert out["budgetCompliant"] is True
    assert out["sandboxCompliant"] is True
    assert out["budgetAccounting"]["peakMemoryMb"]["headroom"]==384.0


def test_over_budget_classified():
    out=evaluate_runtime_attestation(decision(),job(),payload(peakMemoryMb=1024))
    assert out["classification"]=="budget-exceeded"
    assert any(x["check"]=="budget-peakMemoryMb" and x["status"]=="fail" for x in out["checks"])


def test_sandbox_deviation_classified():
    p=payload(); p.sandboxAttestation.networkMode="server-routed-only"
    out=evaluate_runtime_attestation(decision(),job(),p)
    assert out["classification"]=="sandbox-deviation"
    assert out["sandboxCompliant"] is False


def test_missing_runtime_metric_is_incomplete():
    p=payload(); p.observedUsage.cpuCoreSeconds=None
    out=evaluate_runtime_attestation(decision(),job(),p)
    assert out["classification"]=="incomplete"
    assert out["budgetCompliant"] is False


def test_failed_job_classified_execution_failed():
    out=evaluate_runtime_attestation(decision(),job("failed"),payload())
    assert out["classification"]=="execution-failed"


def test_public_contract_and_routes():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    main=(root/'backend/app/main.py').read_text()
    security=(root/'backend/app/security.py').read_text()
    wp=(root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
    assert 'Depends(require_runtime_attestation_identity)' in main
    assert 'X-SC-Runtime-Attestation-Token' in security
    assert '/backend-runtime-execution-attestations' in wp
    assert '/backend-runtime-handoff-receipts/(?P<receipt_id>' not in wp or '/attest' not in wp


def test_migration_has_immutable_one_attestation_per_handoff():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    sql=(root/'backend/migrations/009_runtime_enforcement_telemetry_attestations.sql').read_text()
    assert 'workspace_runtime_execution_attestations' in sql
    assert 'workspace_runtime_execution_attestation_receipt_idx' in sql
    assert 'UNIQUE INDEX' in sql
    assert 'TO sc_workspace' in sql


def test_runtime_attestation_auth_is_separate_from_service_token():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    config=(root/'backend/app/config.py').read_text()
    compose=(root/'backend/docker-compose.example.yml').read_text()
    assert 'runtime_attestation_token' in config
    assert 'SC_WORKSPACE_RUNTIME_ATTESTATION_TOKEN' in compose
    assert 'runtime_attestation_token_configured' in config


def test_release_lineage_is_v280():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    dep=(root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php').read_text()
    cert=(root/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-production-certification.php').read_text()
    assert "const PREVIOUS_RELEASE = '2.8.0';" in dep
    assert "const ROLLBACK_RELEASE = '2.8.0';" in dep
    assert "const PREVIOUS_RELEASE = '2.8.0';" in cert
    assert "const ROLLBACK_RELEASE = '2.8.0';" in cert


def test_attestation_cannot_relax_policy_contract():
    from pathlib import Path
    import json
    root=Path(__file__).resolve().parents[1]
    schema=json.loads((root/'schemas/sc-workspace-runtime-execution-attestation-v1.schema.json').read_text())
    props=schema['properties']
    assert props['policyRelaxationAllowedByAttestation']['const'] is False
    assert props['wordpressAttestationSubmissionAllowed']['const'] is False
    assert props['terminalJobRequired']['const'] is True
