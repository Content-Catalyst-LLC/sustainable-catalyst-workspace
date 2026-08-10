#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.52.0.json').read_text());REG=json.loads((ROOT/'registry/workspace-product-record-v0.52.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.52.0.js').read_text();HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-tasks-v1.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.52.0.css').read_text()
def check(ok,msg):
 if not ok: print('FAIL -',msg);sys.exit(1)
 print('PASS -',msg)
check('Version: 0.52.0' in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.52.0','0.51.0','Research Tasks & Workflow State'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['schema_migration_required'] is False,'schema-stable boundary')
check(MAN['research_task_schema']=='sc-workspace-research-task/1.0' and MAN['research_task_library_schema']=='sc-workspace-research-task-library/1.0','task schemas')
check('data-scw-research-tasks' in PHP and 'data-scw-task-form' in PHP and 'data-scw-task-list' in PHP,'task UI rendered')
check("'/research-tasks-contract'" in PHP and 'public function research_tasks_contract()' in PHP,'public task contract')
check('sc-workspace-research-tasks-v1.js' in PHP and 'SCWorkspaceResearchTasks' in HELP,'task runtime enqueued')
check('targetFromEntry' in HELP and 'historyEvent' in HELP and 'UNRESOLVED TARGET' in JS,'pointer/history/unresolved behavior')
check(MAN['governance']['research_tasks_automatic_creation'] is False and MAN['governance']['research_tasks_automatic_completion'] is False and MAN['governance']['research_tasks_automatic_canonical_mutation'] is False,'no automatic task/canonical mutation')
check(MAN['governance']['editorial_header_rule_px']==4 and '.scw-editorial-header-bar{height:4px' in CSS,'4px editorial rule retained')
check(REG['public_version']=='0.52.0' and REG['previous_version']=='0.51.0','registry lineage')
check((ROOT/'history/release-manifest-v0.51.0.json').exists(),'v0.51 history retained')
print('PASS - v0.52.0 release validator')
