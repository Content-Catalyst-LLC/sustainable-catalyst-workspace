from pathlib import Path
import json

import pytest
from pydantic import ValidationError

from app.policy import TRUST_ORDER, _operation_allowed, _pinned_container
from app.schemas import ExecutionPolicyStoreRequest, ReproductionExecutionPlanCreateRequest, ResourceBudget, RuntimeAdapterStoreRequest

ROOT=Path(__file__).resolve().parents[1]


def test_v280_identity_and_lineage():
    plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
    assert 'Version: 2.8.0' in plugin
    manifest=json.loads((ROOT/'release-manifest-v2.8.0.json').read_text())
    assert manifest['version']=='2.8.0'
    assert manifest['previous_version']=='2.7.0'
    assert manifest['release_name']=='Execution Policy, Resource Budgets & Runtime Sandboxing'


def test_v280_migration_creates_policy_tables_and_adapter_trust():
    models=(ROOT/'backend/app/models.py').read_text()
    migration=(ROOT/'backend/migrations/008_execution_policy_resource_budgets_sandboxing.sql').read_text()
    for token in ['workspace_execution_policy_heads','workspace_execution_policy_revisions','workspace_execution_policy_decisions']:
        assert token in models and token in migration
    assert 'trust_level' in models
    assert 'ADD COLUMN IF NOT EXISTS trust_level' in migration
    assert 'GRANT SELECT, INSERT, UPDATE, DELETE' in migration


def test_execution_policy_schema_has_bounded_resources_and_hard_denials():
    p=ExecutionPolicyStoreRequest.model_validate({
        'schema':'sc-workspace-execution-policy/1.0',
        'policyId':'bounded-workspace',
        'name':'Bounded Workspace',
        'allowedTargetProducts':['workspace'],
        'allowedOperations':['workspace.echo'],
        'minimumAdapterTrust':'bounded',
        'resourceLimits':{'cpuCores':1,'memoryMb':512,'wallSeconds':60,'outputBytes':1048576,'pids':32,'tempStorageMb':128},
        'sandboxMode':'metadata-gate',
        'networkMode':'none',
    })
    assert p.resourceLimits.wallSeconds == 60
    assert p.allowHostFilesystem is False
    assert p.allowDockerSocket is False
    assert p.allowPrivileged is False


def test_execution_policy_cannot_enable_privileged_or_host_access():
    for field in ('allowHostFilesystem','allowDockerSocket','allowPrivileged'):
        data={'schema':'sc-workspace-execution-policy/1.0','policyId':'unsafe','name':'Unsafe',field:True}
        with pytest.raises(ValidationError):
            ExecutionPolicyStoreRequest.model_validate(data)


def test_resource_budget_has_ceiling_validation():
    with pytest.raises(ValidationError):
        ResourceBudget.model_validate({'cpuCores':129})
    with pytest.raises(ValidationError):
        ResourceBudget.model_validate({'memoryMb':32})
    with pytest.raises(ValidationError):
        ResourceBudget.model_validate({'wallSeconds':0})


def test_runtime_adapter_has_explicit_trust_level():
    p=RuntimeAdapterStoreRequest.model_validate({
        'schema':'sc-workspace-runtime-adapter/1.0','adapterId':'python-bounded','name':'Python','trustLevel':'bounded'
    })
    assert p.trustLevel == 'bounded'
    assert TRUST_ORDER['untrusted'] < TRUST_ORDER['bounded'] < TRUST_ORDER['trusted']


def test_execution_plan_requires_policy_and_budget_contract():
    fields=ReproductionExecutionPlanCreateRequest.model_fields
    assert fields['executionPolicyRef'].is_required()
    assert 'resourceBudget' in fields
    assert 'routeUrl' not in fields
    assert 'credentials' not in fields


def test_operation_allowlist_is_fail_closed():
    assert _operation_allowed([], 'workspace.echo') is False
    assert _operation_allowed(['workspace.echo'], 'workspace.echo') is True
    assert _operation_allowed(['*'], 'workspace.echo') is True
    assert _operation_allowed(['lab.run'], 'workspace.echo') is False


def test_pinned_container_requires_digest_identity():
    class A: pass
    a=A(); a.container_json={'image':'python:3.12-slim'}
    assert _pinned_container(a) is False
    a.container_json={'image':'python@sha256:'+'a'*64}
    assert _pinned_container(a) is True


def test_policy_service_enforces_resources_trust_sandbox_and_network():
    service=(ROOT/'backend/app/policy.py').read_text()
    for token in ['target-product-allowed','operation-allowed','adapter-trust','resource-cpuCores','resource-memoryMb','resource-wallSeconds','sandbox-mode','network-policy','no-new-privileges','drop-all-capabilities']:
        assert token in service
    for token in ['allowHostFilesystem','allowDockerSocket','allowPrivileged']:
        assert token in service


def test_handoff_revalidates_frozen_policy_decision_before_job_creation():
    control=(ROOT/'backend/app/execution_control.py').read_text()
    assert 'executionPolicyDecisionId' in control
    assert 'executionPolicyDecisionFingerprint' in control
    assert 'Workspace execution policy does not authorize this controlled handoff.' in control
    assert control.index('Workspace execution policy does not authorize this controlled handoff.') < control.index('job_payload = JobCreateRequest.model_validate')


def test_job_handoff_carries_policy_budget_and_sandbox_envelope():
    control=(ROOT/'backend/app/execution_control.py').read_text()
    routing=(ROOT/'backend/app/routing.py').read_text()
    for token in ['"executionPolicy"','"resourceBudget"','"sandbox"']:
        assert token in control
        assert token in routing


def test_main_routes_and_capabilities_are_policy_aware():
    main=(ROOT/'backend/app/main.py').read_text()
    for route in ['/v1/execution-policies','/v1/execution-policy-decisions']:
        assert route in main
    for flag in ['executionPolicyRegistry','executionPolicyDecisions','resourceBudgets','runtimeSandboxing','policyRequiredForControlledHandoffs','adapterTrustLevels']:
        assert flag in main
    for flag in ['hostFilesystemAccessAllowed','dockerSocketAccessAllowed','privilegedExecutionAllowed']:
        assert f'"{flag}": False' in main


def test_wordpress_proxy_and_contract_are_policy_aware():
    workspace=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
    bridge=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php').read_text()
    for token in ['backend-execution-policies','backend-execution-policy-decisions','backend_execution_policy_store']:
        assert token in workspace
    for flag in ['executionPolicyRegistry','resourceBudgets','runtimeSandboxing','policyRequiredForControlledHandoffs']:
        assert flag in bridge


def test_v280_public_contract_is_fail_closed():
    contract=json.loads((ROOT/'schemas/sc-workspace-execution-policy-v1.schema.json').read_text())
    props=contract['properties']
    assert props['version']['const']=='2.8.0'
    assert props['policyRequiredForControlledHandoffs']['const'] is True
    assert props['humanAuthorizedDispatch']['const'] is True
    assert props['clientSuppliedRuntimeUrlsAllowed']['const'] is False
    assert props['clientSuppliedRuntimeCredentialsAllowed']['const'] is False
    assert props['hostFilesystemAccessAllowed']['const'] is False
    assert props['dockerSocketAccessAllowed']['const'] is False
    assert props['privilegedExecutionAllowed']['const'] is False
    assert props['arbitraryCodeExecution']['const'] is False
