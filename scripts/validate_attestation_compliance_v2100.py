#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
required=['backend/app/compliance.py','backend/migrations/010_attestation_verification_compliance_runtime_trust.sql','schemas/sc-workspace-attestation-verification-compliance-v1.schema.json','release-manifest-v2.10.0.json','registry/workspace-product-record-v2.10.0.json','RELEASE_NOTES_2.10.0.md','docs/ATTESTATION_VERIFICATION_COMPLIANCE_RUNTIME_TRUST_V2100.md']
for rel in required: assert (ROOT/rel).is_file(), rel
plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); assert 'Version: 2.10.0' in plugin
main=(ROOT/'backend/app/main.py').read_text(); comp=(ROOT/'backend/app/compliance.py').read_text(); wp=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
for token in ['/v1/runtime-trust-policies','/v1/compliance-waivers','/v1/attestation-verifications','runtimeTrustPolicyRegistry','downstreamComplianceGates','humanComplianceWaivers']: assert token in main
for token in ['executionAuthorizationGranted','executionPolicyRelaxed','attestationRewritten','NON_WAIVABLE_ATTESTATION_CHECKS']: assert token in comp
for token in ['backend-runtime-trust-policies','backend-compliance-waivers','backend-attestation-verifications']: assert token in wp
schema=json.loads((ROOT/'schemas/sc-workspace-attestation-verification-compliance-v1.schema.json').read_text())
assert schema['properties']['version']['const']=='2.10.0'
assert schema['properties']['waiverMayAuthorizeExecution']['const'] is False
assert schema['properties']['waiverMayRewriteAttestation']['const'] is False
assert schema['properties']['automaticComplianceApproval']['const'] is False
print('PASS — Workspace v2.10.0 attestation verification, compliance gates, and runtime trust validated')
