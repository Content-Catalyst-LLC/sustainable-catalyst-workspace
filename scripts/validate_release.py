#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAN = json.loads((ROOT / 'release-manifest-v0.46.1.json').read_text())
REG = json.loads((ROOT / 'registry/workspace-product-record-v0.46.1.json').read_text())
PREV = json.loads((ROOT / 'history/release-manifest-v0.46.0.json').read_text())
MAIN = (ROOT / 'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.46.1.js').read_text()
INTER = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-interchange-v2.js').read_text()
COMP = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-composition-studio-v1.js').read_text()
REF = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-reference-library-v1.js').read_text()
COLL = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-collections-v1.js').read_text()
SEARCH = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-knowledge-search-v1.js').read_text()
CSS = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.46.1.css').read_text()

def check(value, label):
    if not value:
        raise SystemExit('FAIL - ' + label)
    print('PASS - ' + label)

check('Version: 0.46.1' in MAIN, 'plugin version')
check((MAN['version'], MAN['previous_version'], MAN['release_name']) == ('0.46.1', '0.46.0', 'Workspace Import & Interchange'), 'manifest patch lineage')
check((MAN['storage_schema_version'], MAN['project_schema'], MAN['export_schema']) == (35, 'sc-workspace-project/20.0', 'sc-workspace-project-export/20.0'), 'schema-stable storage 35 / project 20 / export 20')
check(not MAN['schema_migration_required'] and MAN['migration']['schema_stable'] and not MAN['migration']['canonical_data_rewrite'], 'schema-stable visual patch boundary')
check(PREV['version'] == '0.46.0' and PREV['migration']['interchange_only_release'], 'v0.46.0 Interchange history retained')
check(MAN['visual_patch']['editorial_header_rule_from_px'] == 2 and MAN['visual_patch']['editorial_header_rule_to_px'] == 4, '2px to 4px visual patch recorded')
check(MAN['governance']['editorial_header_rule_px'] == 4, '4px editorial header governance contract')
check('.scw-editorial-header-bar{height:4px;background:' in CSS and '@media(max-width:620px){.scw-editorial-header-bar{height:4px}' in CSS, '4px editorial header rule desktop and mobile')
check('.scw-editorial-header-bar{height:12px' not in CSS and '.scw-editorial-header-bar{height:9px' not in CSS, 'legacy 12px/9px bar remains removed')
check('/wp-json/sc-workspace/v1/interoperability-contract' in MAN['rest_routes'] and "'schema' => 'sc-workspace-interoperability-contract/2.0'" in PHP, 'v0.46 Interoperability REST contract retained')
check(MAN['interchange_v2']['profiles'] == ['workspace-json', 'obsidian-markdown', 'notion-csv', 'zotero-csl-json', 'portable-project'], 'five interchange profiles retained')
check(all(token in INTER for token in ('function workspaceJson', 'function obsidianMarkdown', 'function notionCsv', 'function zoteroCslJson', 'function detectProfile', 'function importDescriptors', 'function importReport', 'function exportProject')), 'Interchange runtime helpers retained')
check(not MAN['interchange_v2']['automatic_overwrite'] and MAN['interchange_v2']['staged_review_required'], 'staged review and no silent overwrite retained')
check('function normalizeDraft' in COMP and 'function documentPayload' in COMP, 'v0.45 Composition Studio retained')
check('function referenceFromEntry' in REF and 'function format(raw' in REF, 'v0.44 Citation Library retained')
check('function smartCollection' in COLL and 'function dashboard(entries,state,searchApi,current={})' in COLL, 'v0.43 Research Collections retained')
check('function search(entries,prefs={},state={})' in SEARCH and 'function related(target,entries,state)' in SEARCH, 'v0.42 Advanced Retrieval retained')
check((REG['public_version'], REG['previous_version']) == ('0.46.1', '0.46.0'), 'registry patch lineage')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0461'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0461'" in REGPHP and 'LEGACY_PENDING_KEY_V0460' in REGPHP, 'registry current and legacy retry lineage')
check((ROOT / 'history/release-manifest-v0.46.0.json').exists() and (ROOT / 'history/workspace-product-record-v0.46.0.json').exists(), 'v0.46.0 history preserved')
files = list((ROOT / 'schemas').glob('*.json')) + [ROOT / 'release-manifest-v0.46.1.json', ROOT / 'registry/workspace-product-record-v0.46.1.json']
for path in files:
    json.loads(path.read_text())
print(f'PASS - {len(files)} JSON schema/release records')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.46.1 — Editorial Header Rule Balance')
