#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
required=["backend/julia-runtime/Dockerfile","backend/julia-runtime/service.py","backend/julia-runtime/runner.jl","backend/migrations/014_julia_simulation_numerical_runtime.sql","schemas/sc-workspace-julia-simulation-runtime-v1.schema.json","tests/test_julia_simulation_numerical_runtime_v2140.py","registry/workspace-product-record-v2.14.0.json","release-manifest-v2.14.0.json","RELEASE_NOTES_2.14.0.md"]
missing=[x for x in required if not (ROOT/x).is_file()]
assert not missing, f"missing v2.14 files: {missing}"
assert 'service_version: str = "2.14.0"' in (ROOT/'backend/app/config.py').read_text()
assert 'Version: 2.14.0' in (ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
m=json.loads((ROOT/'release-manifest-v2.14.0.json').read_text()); assert m['previous_version']=='2.13.0'; assert m['julia_runtime']['operation_count']==8; assert m['julia_runtime']['arbitrary_code_execution'] is False
print('PASS — Workspace v2.14.0 Julia simulation/numerical runtime validated')
