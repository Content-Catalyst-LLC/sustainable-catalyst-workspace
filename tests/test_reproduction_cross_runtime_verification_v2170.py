from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_release_contract():
    assert (ROOT/'backend/migrations/017_reproduction_cross_runtime_verification.sql').is_file()
    assert (ROOT/'backend/app/cross_runtime_verification.py').is_file()
    assert (ROOT/'registry/workspace-product-record-v2.17.0.json').is_file()
    assert (ROOT/'schemas/sc-workspace-cross-runtime-verification-receipt-v1.schema.json').is_file()
    assert 'Version: 2.17.0' in (ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
