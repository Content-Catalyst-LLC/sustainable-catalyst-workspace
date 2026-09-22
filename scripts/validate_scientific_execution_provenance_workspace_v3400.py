#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def req(rel, needle):
    text=(ROOT/rel).read_text(); ok=needle in text; checks.append((ok,f'{rel}: {needle}'))
req('backend/app/config.py','3.4.0')
req('backend/app/execution_provenance.py','sc-workspace-scientific-execution-provenance-workspace/1.0')
req('backend/migrations/035_scientific_execution_provenance_workspace.sql','workspace_scientific_execution_provenance_snapshots')
req('backend/app/main.py','/v1/execution-provenance/projects/{project_id}/runs/{run_id}')
req('backend/app/client_contracts.py','executionProvenanceSnapshotCreate')
req('wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php','Version: 3.4.0')
req('wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php','sc-workspace-execution-provenance-v3400.js')
req('backend/deploy_workspace_backend_v3_4_0_vps.sh',"d['version']=='3.4.0'")
req('backend/deploy_workspace_backend_v3_4_0_vps.sh',"typedEndpointCount']==64")
req('backend/deploy_workspace_backend_v3_4_0_vps.sh','033_unified_research_project_context.sql')
req('backend/deploy_workspace_backend_v3_4_0_vps.sh','034_research_session_object_binding_runtime.sql')
req('backend/deploy_workspace_backend_v3_4_0_vps.sh','035_scientific_execution_provenance_workspace.sql')
req('backend/docker-compose.example.yml','name: sc-workspace-runtime')
if (ROOT/'catalystanalyticsr').exists():
    checks.append((False,'repository must not contain accidental catalystanalyticsr gitlink/directory'))
failed=[m for ok,m in checks if not ok]
if failed:
    print('\n'.join('FAIL: '+m for m in failed)); sys.exit(1)
print('PASS: Workspace v3.4.0 Scientific Execution & Provenance Workspace release contract')
