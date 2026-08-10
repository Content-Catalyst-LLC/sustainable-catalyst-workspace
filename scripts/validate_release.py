#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.54.0.json').read_text());REG=json.loads((ROOT/'registry/workspace-product-record-v0.54.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text();HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-shared-review-handoff-v1.js').read_text();UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-shared-review-handoff-ui-v1.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.54.0.css').read_text()
def check(ok,msg):
 if not ok: print('FAIL -',msg);sys.exit(1)
 print('PASS -',msg)
check('Version: 0.54.0' in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.54.0','0.53.0','Shared Review & Research Handoff'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['schema_migration_required'] is False,'schema-stable boundary')
check(MAN['shared_review_handoff_schema']=='sc-workspace-shared-review-handoff/1.0' and MAN['shared_review_package_schema']=='sc-workspace-shared-review-package/1.0' and MAN['shared_review_response_schema']=='sc-workspace-shared-review-response/1.0','shared review schemas')
check('data-scw-shared-review-handoff' in PHP and 'data-scw-handoff-form' in PHP and 'data-scw-reviewer-response-form' in PHP,'shared review UI rendered')
check("'/shared-review-handoff-contract'" in PHP and 'public function shared_review_handoff_contract()' in PHP,'public shared review contract')
check('sc-workspace-shared-review-handoff-v1.js' in PHP and 'sc-workspace-shared-review-handoff-ui-v1.js' in PHP,'shared review runtimes enqueued')
check('frozenSnapshot:true' in HELP and 'validateResponse' in HELP and 'stageResponse' in HELP and 'commitResponse' in HELP,'frozen scope and staged response flow')
check(MAN['governance']['shared_review_response_must_match_package'] is True and MAN['governance']['shared_review_import_mutates_canonical_project'] is False and MAN['governance']['shared_review_live_coediting'] is False,'review governance boundaries')
check(MAN['governance']['editorial_header_rule_px']==4 and '.scw-editorial-header-bar{height:4px' in CSS,'4px editorial rule retained')
check(REG['public_version']=='0.54.0' and REG['previous_version']=='0.53.0','registry lineage')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0540'" in REGPHP and 'LEGACY_PENDING_KEY_V0530' in REGPHP,'registry recovery lineage')
check((ROOT/'history/release-manifest-v0.53.0.json').exists(),'v0.53 history retained')
print('PASS - v0.54.0 release validator')
