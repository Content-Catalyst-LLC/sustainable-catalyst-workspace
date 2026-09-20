from pathlib import Path
from app.config import Settings
from app.interchange import OPERATIONS, operation_catalog

def test_version_and_registry():
    assert Settings().service_version == "2.32.0"
    assert len(OPERATIONS)==8
    assert {x["operation"] for x in operation_catalog()}==set(OPERATIONS)

def test_runtime_package_contract():
    root=Path(__file__).resolve().parents[1]
    svc=(root/"interchange-runtime/service.py").read_text()
    assert 'pyarrow' in svc and 'arrow-ipc-stream' in svc and 'parquet' in svc
    assert 'arbitraryCodeExecution":False' in svc
    compose=(root/"docker-compose.example.yml").read_text()
    assert 'sc-workspace-interchange-runtime' in compose
    assert 'read_only: true' in compose
    assert (root/"migrations/016_native_arrow_parquet_interchange.sql").is_file()
