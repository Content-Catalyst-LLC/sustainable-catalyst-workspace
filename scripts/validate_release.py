#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAN = json.loads((ROOT / 'release-manifest-v0.46.0.json').read_text())
REG = json.loads((ROOT / 'registry/workspace-product-record-v0.46.0.json').read_text())
PREV = json.loads((ROOT / 'history/release-manifest-v0.45.0.json').read_text())
MAIN = (ROOT / 'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP = (ROOT / 'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.46.0.js').read_text()
INTER = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-interchange-v2.js').read_text()
COMP = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-composition-studio-v1.js').read_text()
REF = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-reference-library-v1.js').read_text()
COLL = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-collections-v1.js').read_text()
SEARCH = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-knowledge-search-v1.js').read_text()
CSS = (ROOT / 'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.46.0.css').read_text()

def check(value, label):
    if not value:
        raise SystemExit('FAIL - ' + label)
    print('PASS - ' + label)

check('Version: 0.46.0' in MAIN, 'plugin version')
check((MAN['version'], MAN['previous_version'], MAN['release_name']) == ('0.46.0', '0.45.0', 'Workspace Import & Interchange'), 'manifest release lineage')
check((MAN['storage_schema_version'], MAN['project_schema'], MAN['export_schema']) == (35, 'sc-workspace-project/20.0', 'sc-workspace-project-export/20.0'), 'schema-stable storage 35 / project 20 / export 20')
check(not MAN['schema_migration_required'] and MAN['migration']['schema_stable'] and MAN['migration']['interchange_only_release'] and not MAN['migration']['interchange_project_schema_change'] and not MAN['migration']['canonical_data_rewrite'], 'schema-stable interchange boundary')
check(PREV['migration']['composition_studio_only_release'], 'v0.45 Composition Studio history retained')
check('/wp-json/sc-workspace/v1/interoperability-contract' in MAN['rest_routes'] and "'schema' => 'sc-workspace-interoperability-contract/2.0'" in PHP and "'interchange_export_schema' => 'sc-workspace-interchange/2.0'" in PHP, 'Interoperability REST contract v2')
check(MAN['interchange_profile_schema'] == 'sc-workspace-interchange-profile/1.0' and MAN['interchange_bundle_schema'] == 'sc-workspace-interchange/2.0' and MAN['interchange_import_report_schema'] == 'sc-workspace-interchange-import-report/1.0', 'Interchange schemas')
for name in ('sc-workspace-interchange-profile-v1.schema.json', 'sc-workspace-interchange-bundle-v2.schema.json', 'sc-workspace-interchange-import-report-v1.schema.json'):
    json.loads((ROOT / 'schemas' / name).read_text())
check(MAN['interchange_v2']['profiles'] == ['workspace-json', 'obsidian-markdown', 'notion-csv', 'zotero-csl-json', 'portable-project'], 'five interchange profiles')
check(all(token in INTER for token in ('function workspaceJson', 'function obsidianMarkdown', 'function notionCsv', 'function zoteroCslJson', 'function detectProfile', 'function importDescriptors', 'function importReport', 'function exportProject')), 'Interchange runtime helpers')
check(all(token in PHP for token in ('data-scw-interoperability-export-profile', 'Obsidian-ready Markdown', 'Notion-style CSV', 'Zotero / CSL JSON')), 'Interchange presentation profiles')
check('interoperabilityExportProfile' in JS and 'specializedInteropObjects' in JS and 'stageExternalContent' in JS, 'Interchange integration')
iv2 = MAN['interchange_v2']
check(iv2['staged_review_required'] and not iv2['automatic_overwrite'] and not iv2['automatic_trust_elevation'], 'staged review / no silent overwrite / no trust elevation')
check(not iv2['external_network_lookup'] and not iv2['automatic_ai'] and not iv2['server_import_pipeline'], 'no network lookup / AI / server import pipeline')
check(iv2['portable_project_mode'] == 'import-as-new-local-copy' and "profile==='portable-project'" in JS and 'portableProjectPackage(project' in JS, 'portable Project import-as-copy retained')
check(MAN['governance']['editorial_header_rule_px'] == 2 and '.scw-editorial-header-bar{height:2px' in CSS and '.scw-editorial-header-bar{height:12px' not in CSS and '.scw-editorial-header-bar{height:9px' not in CSS, 'site-aligned 2px editorial header rule')
check('function normalizeDraft' in COMP and 'function documentPayload' in COMP and 'function compositionApi()' in JS, 'v0.45 Composition Studio retained')
check('function referenceFromEntry' in REF and 'function format(raw' in REF, 'v0.44 Citation Library retained')
check('function smartCollection' in COLL and 'function dashboard(entries,state,searchApi,current={})' in COLL, 'v0.43 Research Collections retained')
check('function search(entries,prefs={},state={})' in SEARCH and 'function related(target,entries,state)' in SEARCH, 'v0.42 Advanced Retrieval retained')
check((REG['public_version'], REG['previous_version']) == ('0.46.0', '0.45.0'), 'registry lineage')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0460'" in REGPHP and 'LEGACY_PENDING_KEY_V0450' in REGPHP, 'registry retry lineage')
check((ROOT / 'history/release-manifest-v0.45.0.json').exists() and (ROOT / 'history/workspace-product-record-v0.45.0.json').exists(), 'v0.45 history preserved')
files = list((ROOT / 'schemas').glob('*.json')) + [ROOT / 'release-manifest-v0.46.0.json', ROOT / 'registry/workspace-product-record-v0.46.0.json']
for path in files:
    json.loads(path.read_text())
print(f'PASS - {len(files)} JSON schema/release records')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.46.0 — Workspace Import & Interchange')
