from pathlib import Path
import json

from app.runtime_adapters import _norm_version

ROOT = Path(__file__).resolve().parents[1]


def test_v260_identity_and_lineage():
    plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
    assert 'Version: 2.6.0' in plugin
    manifest=json.loads((ROOT/'release-manifest-v2.6.0.json').read_text())
    assert manifest['version']=='2.6.0'
    assert manifest['previous_version']=='2.5.0'
    assert manifest['release_name']=='Runtime Adapter Registry & Reproduction Verification'


def test_runtime_adapter_database_contract():
    models=(ROOT/'backend/app/models.py').read_text()
    migration=(ROOT/'backend/migrations/006_runtime_adapter_reproduction_verification.sql').read_text()
    for token in ['workspace_runtime_adapter_heads','workspace_runtime_adapter_revisions','workspace_reproduction_plans','workspace_reproduction_verifications','runtime_adapter_ref','runtime_adapter_fingerprint']:
        assert token in models or token in migration
    assert 'GRANT SELECT, INSERT, UPDATE, DELETE' in migration


def test_runtime_adapter_routes_and_run_linkage():
    main=(ROOT/'backend/app/main.py').read_text(); schemas=(ROOT/'backend/app/schemas.py').read_text(); registry=(ROOT/'backend/app/registry.py').read_text()
    for route in ['/v1/runtime-adapters','/v1/runtime-adapters/{adapter_id}/compatibility','/v1/reproduction-plans','/v1/reproduction-verifications']:
        assert route in main
    assert 'runtimeAdapterRef' in schemas
    assert 'resolve_runtime_adapter_ref' in registry


def test_runtime_adapters_do_not_accept_arbitrary_commands():
    schemas=(ROOT/'backend/app/schemas.py').read_text(); service=(ROOT/'backend/app/runtime_adapters.py').read_text()
    assert 'commandTemplate' not in schemas
    assert 'shellCommand' not in schemas
    assert 'arbitraryCommandExecution' in service
    assert '"arbitraryCommandExecution": False' in service


def test_reproduction_verification_is_digest_based_and_bounded():
    repro=(ROOT/'backend/app/reproduction.py').read_text()
    assert 'metadata-and-content-digests' in repro
    assert 'classification="exact"' in repro
    assert 'classification="compatible"' in repro
    assert 'classification="divergent"' in repro
    assert 'classification="incomplete"' in repro
    assert 'comparisonExecuted' in repro


def test_runtime_version_normalization():
    assert _norm_version('3.12.4') == (3,12,4)
    assert _norm_version('v4.4.1') == (4,4,1)
    assert _norm_version('') is None


def test_wordpress_runtime_adapter_and_reproduction_proxies_exist():
    workspace=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
    bridge=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php').read_text()
    for token in ['backend-runtime-adapters','backend-reproduction-plans','backend-reproduction-verifications']:
        assert token in workspace
    for flag in ['runtimeAdapterRegistry','runtimeCompatibilityChecks','reproductionPlans','reproductionVerification','deterministicRerunComparison']:
        assert flag in bridge


def test_v260_contract_is_bounded():
    contract=json.loads((ROOT/'schemas/sc-workspace-runtime-adapter-reproduction-v1.schema.json').read_text())
    props=contract['properties']
    assert props['version']['const']=='2.6.0'
    assert props['supportedRuntimeFamilies']['const']==['python','r','julia','custom']
    assert props['comparisonMode']['const']=='metadata-and-content-digests'
    assert props['automaticReexecution']['const'] is False
    assert props['arbitraryCodeExecution']['const'] is False
