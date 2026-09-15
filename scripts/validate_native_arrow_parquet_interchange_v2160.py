from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert 'service_version: str = "2.16.0"' in (ROOT/'backend/app/config.py').read_text()
assert (ROOT/'backend/migrations/016_native_arrow_parquet_interchange.sql').is_file()
svc=(ROOT/'backend/interchange-runtime/service.py').read_text()
for term in ('pyarrow','workspace.interchange.parquet.write','workspace.interchange.verify','arrow-ipc-stream'):
    assert term in svc, term
compose=(ROOT/'backend/docker-compose.example.yml').read_text()
assert 'sc-workspace-interchange-runtime' in compose and 'internal: true' in compose
print('PASS - v2.16.0 native Arrow/Parquet interchange contract')
