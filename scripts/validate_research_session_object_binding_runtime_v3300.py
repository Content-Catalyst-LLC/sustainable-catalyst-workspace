#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def req(rel, needle):
    text=(ROOT/rel).read_text(); ok=needle in text; checks.append((ok,f'{rel}: {needle}'))
req('backend/app/config.py','3.3.0')
req('backend/app/research_session_bindings.py','sc-workspace-research-session-object-binding-runtime/1.0')
req('backend/migrations/034_research_session_object_binding_runtime.sql','workspace_research_session_object_bindings')
req('backend/app/main.py','/v1/research-bindings/projects/{project_id}/reconcile')
req('backend/app/client_contracts.py','researchSessionBindingsReconcile')
req('wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php','Version: 3.3.0')
req('backend/deploy_workspace_backend_v3_3_0_vps.sh',"d['version']=='3.3.0'")
req('backend/deploy_workspace_backend_v3_3_0_vps.sh',"typedEndpointCount']==59")
req('backend/deploy_workspace_backend_v3_3_0_vps.sh','033_unified_research_project_context.sql')
req('backend/deploy_workspace_backend_v3_3_0_vps.sh','034_research_session_object_binding_runtime.sql')
failed=[m for ok,m in checks if not ok]
if failed:
    print('\n'.join('FAIL: '+m for m in failed)); sys.exit(1)
print('PASS: Workspace v3.3.0 Research Session & Object Binding Runtime release contract')
