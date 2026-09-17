from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert 'service_version: str = "2.17.0"' in (ROOT/'backend/app/config.py').read_text()
assert (ROOT/'backend/migrations/017_reproduction_cross_runtime_verification.sql').is_file()
svc=(ROOT/'backend/app/cross_runtime_verification.py').read_text()
for needle in ('tolerance-aware-json','exact-digest','equivalentOutputs','arbitraryCodeExecution'):
    assert needle in svc, needle
main=(ROOT/'backend/app/main.py').read_text()
for needle in ('/v1/reproduction/cross-runtime/profiles','/v1/reproduction/cross-runtime/verifications','crossRuntimeReproductionVerification'):
    assert needle in main, needle
wp=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
assert 'backend-cross-runtime-verifications' in wp
assert (ROOT/'registry/workspace-product-record-v2.17.0.json').is_file()
print('PASS - v2.17.0 reproduction & cross-runtime verification contract')
