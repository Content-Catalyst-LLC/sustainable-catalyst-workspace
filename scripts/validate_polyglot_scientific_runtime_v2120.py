#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
required=[
'backend/app/polyglot.py','backend/migrations/012_polyglot_scientific_runtime_fabric.sql','schemas/sc-workspace-polyglot-runtime-v1.schema.json',
'tests/test_polyglot_scientific_runtime_v2120.py','scripts/deploy_workspace_backend_v2_12_0_vps.sh','release-manifest-v2.12.0.json',
'registry/workspace-product-record-v2.12.0.json','wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.12.0.js','wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.12.0.css']
for rel in required: assert (ROOT/rel).is_file(), f'missing {rel}'
config=(ROOT/'backend/app/config.py').read_text(); main=(ROOT/'backend/app/main.py').read_text(); poly=(ROOT/'backend/app/polyglot.py').read_text(); routing=(ROOT/'backend/app/routing.py').read_text(); compose=(ROOT/'backend/docker-compose.example.yml').read_text(); plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); bridge=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-backend.php').read_text(); ws=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); dep=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-deployment.php').read_text()
assert 'service_version: str = "2.12.0"' in config
assert 'Version: 2.12.0' in plugin
assert "const PREVIOUS_RELEASE = '2.11.0';" in dep and "const ROLLBACK_RELEASE = '2.11.0';" in dep
for x in ['polyglotScientificRuntimeFabric','arrowCompatibleInterchange','polyglotExecutionReceipts','@app.get("/v1/polyglot/runtimes")','@app.get("/v1/polyglot/operations")']: assert x in main
for x in ['python','sql','r','julia','wasm','workspace.polyglot.sql.aggregate','workspace.polyglot.r.statistics','workspace.polyglot.julia.simulation','workspace.polyglot.wasm.invoke']: assert x in poly
for bad in ['subprocess','shell=True','eval(','exec(']: assert bad not in poly
assert 'row.operation.startswith("workspace.polyglot.")' in routing
for x in ['SC_WORKSPACE_RUNTIME_R_URL','SC_WORKSPACE_RUNTIME_JULIA_URL','SC_WORKSPACE_RUNTIME_WASM_URL','read_only: true','no-new-privileges:true']: assert x in compose
for x in ['polyglotScientificRuntimeFabric','polyglotLanguages','arrowCompatibleInterchange','polyglotExecutionReceipts']: assert x in bridge
for x in ['backend-polyglot-runtimes','backend-polyglot-operations','backend-polyglot-receipts','workspace-v2.12.0.js','workspace-v2.12.0.css','polyglot-scientific-runtime-fabric']: assert x in ws
schema=json.loads((ROOT/'schemas/sc-workspace-polyglot-runtime-v1.schema.json').read_text()); assert schema['properties']['version']['const']=='2.12.0'; assert schema['properties']['arbitraryCodeExecution']['const'] is False
manifest=json.loads((ROOT/'release-manifest-v2.12.0.json').read_text()); assert manifest['version']=='2.12.0' and manifest['previous_version']=='2.11.0'
print('PASS — Workspace v2.12.0 polyglot scientific runtime fabric validated')
