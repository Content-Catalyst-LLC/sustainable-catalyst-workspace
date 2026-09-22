#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
required=[
 'backend/app/policy.py','backend/migrations/008_execution_policy_resource_budgets_sandboxing.sql',
 'schemas/sc-workspace-execution-policy-v1.schema.json','release-manifest-v2.8.0.json',
 'registry/workspace-product-record-v2.8.0.json','RELEASE_NOTES_2.8.0.md',
 'docs/EXECUTION_POLICY_RESOURCE_BUDGETS_RUNTIME_SANDBOXING_V280.md'
]
for rel in required:
    assert (ROOT/rel).is_file(), rel
plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
assert 'Version: 2.8.0' in plugin
main=(ROOT/'backend/app/main.py').read_text(); policy=(ROOT/'backend/app/policy.py').read_text(); control=(ROOT/'backend/app/execution_control.py').read_text(); wp=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
for token in ['/v1/execution-policies','/v1/execution-policy-decisions','executionPolicyRegistry','resourceBudgets','runtimeSandboxing']:
    assert token in main
for token in ['adapter-trust','resource-cpuCores','resource-memoryMb','resource-wallSeconds','sandbox-mode','network-policy']:
    assert token in policy
for token in ['executionPolicyDecisionId','executionPolicyDecisionFingerprint','resourceBudget','sandbox']:
    assert token in control
for token in ['backend-execution-policies','backend-execution-policy-decisions']:
    assert token in wp
schema=json.loads((ROOT/'schemas/sc-workspace-execution-policy-v1.schema.json').read_text())
assert schema['properties']['version']['const']=='2.8.0'
for key in ('clientSuppliedRuntimeUrlsAllowed','clientSuppliedRuntimeCredentialsAllowed','hostFilesystemAccessAllowed','dockerSocketAccessAllowed','privilegedExecutionAllowed','arbitraryCodeExecution'):
    assert schema['properties'][key]['const'] is False
assert schema['properties']['policyRequiredForControlledHandoffs']['const'] is True
print('PASS — Workspace v2.8.0 execution policy, resource budgets, and runtime sandboxing validated')
