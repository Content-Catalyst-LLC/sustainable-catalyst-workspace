from pathlib import Path
import json

from app.schemas import ControlledRuntimeHandoffRequest, ReproductionExecutionPlanCreateRequest

ROOT=Path(__file__).resolve().parents[1]


def test_v270_identity_and_lineage():
    plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
    assert 'Version: 2.7.0' in plugin
    manifest=json.loads((ROOT/'release-manifest-v2.7.0.json').read_text())
    assert manifest['version']=='2.7.0'
    assert manifest['previous_version']=='2.6.0'
    assert manifest['release_name']=='Reproduction Execution Plans & Controlled Runtime Handoffs'


def test_v270_database_contract_and_grants():
    models=(ROOT/'backend/app/models.py').read_text(); migration=(ROOT/'backend/migrations/007_controlled_runtime_handoffs.sql').read_text()
    for token in ['workspace_reproduction_execution_plans','workspace_runtime_handoff_receipts']:
        assert token in models and token in migration
    assert 'GRANT SELECT, INSERT, UPDATE, DELETE' in migration


def test_execution_plan_schema_has_no_route_url_or_credentials():
    fields=ReproductionExecutionPlanCreateRequest.model_fields
    assert 'targetProduct' not in fields
    assert 'operation' not in fields
    assert 'routeUrl' not in fields
    assert 'token' not in fields
    assert 'credentials' not in fields


def test_handoff_requires_literal_human_authorization():
    payload={"schema":"sc-workspace-controlled-runtime-handoff/1.0","humanAuthorized":True}
    parsed=ControlledRuntimeHandoffRequest.model_validate(payload)
    assert parsed.humanAuthorized is True
    try:
        ControlledRuntimeHandoffRequest.model_validate({"schema":"sc-workspace-controlled-runtime-handoff/1.0","humanAuthorized":False})
    except Exception:
        pass
    else:
        raise AssertionError('false human authorization must be rejected')


def test_control_service_freezes_target_and_operation_and_has_separate_dispatch():
    service=(ROOT/'backend/app/execution_control.py').read_text()
    assert 'frozenTargetAndOperation' in service
    assert 'create_execution_plan' in service
    assert 'dispatch_execution_plan' in service
    assert 'automaticDispatch' in service
    assert 'clientSuppliedRouteUrlAllowed' in service
    assert 'credentialsAcceptedFromClient' in service


def test_runtime_adapter_capability_and_route_readiness_are_required():
    service=(ROOT/'backend/app/execution_control.py').read_text()
    assert 'runtime-adapter-capability' in service
    assert 'server-configured-route' in service
    assert 'runtime-environment-compatibility' in service
    assert 'route_registry()' in service


def test_main_routes_and_capabilities():
    main=(ROOT/'backend/app/main.py').read_text()
    for route in ['/v1/reproduction-execution-plans','/v1/reproduction-execution-plans/{execution_plan_id}/handoff','/v1/runtime-handoff-receipts']:
        assert route in main
    for flag in ['reproductionExecutionPlans','controlledRuntimeHandoffs','humanAuthorizedDispatch','frozenExecutionEnvelope']:
        assert flag in main
    assert '"automaticReproductionExecution": False' in main
    assert '"clientSuppliedRuntimeUrlsAllowed": False' in main


def test_wordpress_proxy_contract():
    workspace=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
    bridge=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php').read_text()
    for token in ['backend-reproduction-execution-plans','backend-runtime-handoff-receipts','backend_reproduction_execution_plan_handoff']:
        assert token in workspace
    for flag in ['reproductionExecutionPlans','controlledRuntimeHandoffs','humanAuthorizedDispatch','automaticReproductionExecution']:
        assert flag in bridge


def test_v270_contract_is_bounded():
    contract=json.loads((ROOT/'schemas/sc-workspace-controlled-runtime-handoff-v1.schema.json').read_text())
    props=contract['properties']
    assert props['version']['const']=='2.7.0'
    assert props['humanAuthorizedDispatch']['const'] is True
    assert props['automaticReproductionExecution']['const'] is False
    assert props['clientSuppliedRuntimeUrlsAllowed']['const'] is False
    assert props['clientSuppliedRuntimeCredentialsAllowed']['const'] is False
    assert props['arbitraryCodeExecution']['const'] is False
