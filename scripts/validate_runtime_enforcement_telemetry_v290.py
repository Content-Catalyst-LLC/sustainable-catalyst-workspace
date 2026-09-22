#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
required=[
 'backend/app/telemetry.py','backend/migrations/009_runtime_enforcement_telemetry_attestations.sql',
 'schemas/sc-workspace-runtime-execution-attestation-v1.schema.json','release-manifest-v2.9.0.json',
 'registry/workspace-product-record-v2.9.0.json','RELEASE_NOTES_2.9.0.md',
 'docs/RUNTIME_ENFORCEMENT_TELEMETRY_BUDGET_ACCOUNTING_ATTESTATIONS_V290.md'
]
for rel in required: assert (ROOT/rel).is_file(), rel
plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); assert 'Version: 2.9.0' in plugin
main=(ROOT/'backend/app/main.py').read_text(); telemetry=(ROOT/'backend/app/telemetry.py').read_text(); security=(ROOT/'backend/app/security.py').read_text(); wp=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
for token in ['/v1/runtime-execution-attestations','/v1/runtime-handoff-receipts/{receipt_id}/attest','runtimeEnforcementTelemetry','budgetAccounting','executionAttestations']: assert token in main
for token in ['budget-cpuCoreSeconds','budget-peakMemoryMb','budget-wallSeconds','budget-outputBytes','sandbox-networkMode','policyDecisionFingerprint']: assert token in telemetry or token.replace('policyDecisionFingerprint','policy_decision_fingerprint') in telemetry
for token in ['X-SC-Runtime-Attestation-Token','require_runtime_attestation_identity']: assert token in security
for token in ['backend-runtime-execution-attestations','backend_runtime_execution_attestations']: assert token in wp
schema=json.loads((ROOT/'schemas/sc-workspace-runtime-execution-attestation-v1.schema.json').read_text())
assert schema['properties']['version']['const']=='2.9.0'
assert schema['properties']['dedicatedRuntimeAttestationCredentialRequired']['const'] is True
assert schema['properties']['browserAttestationSubmissionAllowed']['const'] is False
assert schema['properties']['arbitraryCodeExecution']['const'] is False
print('PASS — Workspace v2.9.0 runtime enforcement telemetry, budget accounting, and execution attestations validated')
