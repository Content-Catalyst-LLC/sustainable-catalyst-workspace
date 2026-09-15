from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_v216_contract():
    assert 'service_version: str = "2.16.0"' in (ROOT/'backend/app/config.py').read_text()
    assert (ROOT/'backend/migrations/016_native_arrow_parquet_interchange.sql').exists()
    svc=(ROOT/'backend/interchange-runtime/service.py').read_text()
    assert svc.count('workspace.interchange.') >= 8
    assert 'pyarrow' in svc and 'parquet' in svc and 'arrow-ipc-stream' in svc
    assert 'client filesystem' not in svc.lower()
