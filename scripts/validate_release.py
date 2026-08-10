#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.53.0.json').read_text());REG=json.loads((ROOT/'registry/workspace-product-record-v0.53.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.53.0.js').read_text();HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-collaboration-architecture-v1.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.53.0.css').read_text()
def check(ok,msg):
 if not ok: print('FAIL -',msg);sys.exit(1)
 print('PASS -',msg)
check('Version: 0.53.0' in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.53.0','0.52.0','Collaboration Architecture Foundation'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['schema_migration_required'] is False,'schema-stable boundary')
check(MAN['collaboration_architecture_schema']=='sc-workspace-collaboration-architecture/1.0' and MAN['shareable_project_contract_schema']=='sc-workspace-shareable-project-contract/1.0','collaboration architecture schemas')
check('data-scw-collaboration-architecture' in PHP and 'data-scw-collab-policy-form' in PHP and 'data-scw-collab-proposal-form' in PHP,'collaboration architecture UI rendered')
check("'/collaboration-architecture-contract'" in PHP and 'public function collaboration_architecture_contract()' in PHP,'public collaboration architecture contract')
check('sc-workspace-collaboration-architecture-v1.js' in PHP and 'SCWorkspaceCollaborationArchitecture' in HELP,'collaboration architecture runtime enqueued')
check('ownerActorId' in HELP and 'capabilitiesForRole' in HELP and 'canonicalMutation:false' in HELP,'ownership/capability/proposal boundary')
check(MAN['governance']['collaboration_policy_grants_server_access'] is False and MAN['governance']['collaboration_proposal_acceptance_mutates_canonical'] is False and MAN['governance']['shareable_project_contract_includes_project_content'] is False,'no server permission/content mutation simulation')
check(MAN['governance']['editorial_header_rule_px']==4 and '.scw-editorial-header-bar{height:4px' in CSS,'4px editorial rule retained')
check(REG['public_version']=='0.53.0' and REG['previous_version']=='0.52.0','registry lineage')
check((ROOT/'history/release-manifest-v0.52.0.json').exists(),'v0.52 history retained')
print('PASS - v0.53.0 release validator')
