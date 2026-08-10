#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.49.0.json').read_text()); REG=json.loads((ROOT/'registry/workspace-product-record-v0.49.0.json').read_text()); PREV=json.loads((ROOT/'history/release-manifest-v0.48.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text(); JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.49.0.js').read_text(); TPL=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-templates-v1.js').read_text(); CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.49.0.css').read_text()
def check(v,label):
 if not v: raise SystemExit('FAIL - '+label)
 print('PASS - '+label)
check('Version: 0.49.0' in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.49.0','0.48.0','Research Templates & Reusable Workflows'),'release lineage')
check((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema'])==(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'),'schema stable')
check(not MAN['schema_migration_required'] and MAN['migration']['schema_stable'] and MAN['migration']['research_templates_only_release'] and not MAN['migration']['canonical_data_rewrite'],'template-only boundary')
check(PREV['version']=='0.48.0' and PREV['release_name']=='Cross-Project Knowledge','v0.48.0 predecessor retained')
check(MAN['research_template_library_schema']=='sc-workspace-research-template-library/1.0' and MAN['research_template_schema']=='sc-workspace-research-template/1.0','template schemas')
check(MAN['research_templates']['built_in_count']==8 and 'Literature Review' in MAN['research_templates']['built_in_templates'],'eight built-in protocols')
check('templateFromWorkflow' in TPL and 'copiesProjectContent:false' in TPL and 'copiesFindings:false' in TPL and 'copiesCompletionStatus:false' in TPL,'structure-only custom capture')
check('Apply structure to this project' in PHP and 'Create project starter' in PHP and 'Save active workflow as template' in PHP,'explicit template UI')
check('helper.createNotebook' in JS and 'helper.createSection' in JS and 'objectTemplate(spec.type,spec.title)' in JS,'workflow/notebook/starter scaffolds')
check('exportPackage' in TPL and 'verifyPackage' in TPL and 'workspace-research-templates.json' in JS,'portable custom template library')
check("'/research-templates-contract'" in PHP and 'research_templates_contract' in PHP,'public template contract')
check(not MAN['governance']['research_templates_store_project_content'] and not MAN['governance']['research_templates_store_findings'] and not MAN['governance']['research_templates_automatic_ai'],'governance boundary')
check('.scw-editorial-header-bar{height:4px' in CSS,'4px editorial header retained')
check((REG['public_version'],REG['previous_version'])==('0.49.0','0.48.0'),'registry lineage')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0490'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0490'" in REGPHP and 'LEGACY_PENDING_KEY_V0480' in REGPHP,'registry retry lineage')
files=list((ROOT/'schemas').glob('*.json'))+[ROOT/'release-manifest-v0.49.0.json',ROOT/'registry/workspace-product-record-v0.49.0.json']
for f in files: json.loads(f.read_text())
print(f'PASS - {len(files)} JSON schema/release records')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.49.0 — Research Templates & Reusable Workflows')
