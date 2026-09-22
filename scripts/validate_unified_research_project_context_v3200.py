#!/usr/bin/env python3
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def req(rel, needle):
    text=(ROOT/rel).read_text(); ok=needle in text; checks.append((ok,f'{rel}: {needle}'))
req('backend/app/config.py','3.2.0')
req('backend/app/unified_research_context.py','sc-workspace-unified-research-project-context/1.0')
req('backend/migrations/033_unified_research_project_context.sql','workspace_unified_research_context_snapshots')
req('backend/app/main.py','/v1/research-context/projects/{project_id}')
req('backend/app/client_contracts.py','unifiedResearchContextSnapshotCreate')
req('wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php','Version: 3.2.0')
req('backend/deploy_workspace_backend_v3_2_0_vps.sh',"d['version']=='3.2.0'")
req('backend/deploy_workspace_backend_v3_2_0_vps.sh',"typedEndpointCount']==55")
failed=[m for ok,m in checks if not ok]
if failed:
    print('\n'.join('FAIL: '+m for m in failed)); sys.exit(1)
print('PASS: Workspace v3.2.0 Unified Research Project Context release contract')
