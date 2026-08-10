#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.55.0.json').read_text());REG=json.loads((ROOT/'registry/workspace-product-record-v0.55.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text();HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-api-embed-v1.js').read_text();UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-api-embed-ui-v1.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.55.0.css').read_text()
def check(v,m):
 if not v: print('FAIL - '+m);sys.exit(1)
 print('PASS - '+m)
check('Version: 0.55.0' in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.55.0','0.54.0','Workspace API & Embed Foundation'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0','schema-stable boundary')
check(MAN['durable_reference_schema']=='sc-workspace-durable-reference/1.0' and MAN['embed_descriptor_schema']=='sc-workspace-embed-descriptor/1.0','api/embed schemas')
check(MAN['api_embed']['canonical_workspace_default']=='private-browser-local' and MAN['api_embed']['live_server_project_api'] is False,'private-by-default boundary')
check(MAN['api_embed']['durable_reference_is_authorization'] is False and 'authorization:false' in HELP,'durable reference not authorization')
check("'/api-embed-contract'" in PHP and 'public function api_embed_contract()' in PHP,'public API/embed contract')
check('data-scw-api-embed' in PHP and 'data-scw-api-create' in PHP and 'data-scw-api-copy-embed' in PHP,'API/embed UI rendered')
check('sc-workspace-api-embed-v1.js' in PHP and 'sc-workspace-api-embed-ui-v1.js' in PHP,'API/embed runtimes enqueued')
check('explicitDisclosure:true' in HELP and 'serverDataEndpoint:false' in HELP and 'noLiveDataFetch:true' in HELP,'static disclosure governance')
check(REG['public_version']=='0.55.0' and REG['previous_version']=='0.54.0','registry lineage')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0550'" in REGPHP and 'LEGACY_PENDING_KEY_V0540' in REGPHP,'registry recovery lineage')
check('.scw-editorial-header-bar{height:4px' in CSS and 'scw-api-embed{margin:24px 0 34px;padding:24px;border:1px solid #dedede;border-top:4px solid #000' in CSS,'4px editorial header retained')
check((ROOT/'history/release-manifest-v0.54.0.json').exists(),'v0.54 manifest preserved')
print('PASS - v0.55.0 release validator')
