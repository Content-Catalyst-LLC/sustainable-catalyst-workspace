from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]

def check(ok, label):
    if not ok:
        print('FAIL - ' + label)
        sys.exit(1)
    print('PASS - ' + label)

main = (ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
php = (ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
reg = (ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
js = (ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.33.0.js').read_text()
notebook = (ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v2.js').read_text()
capture = (ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-source-capture-v1.js').read_text()
field_helper = (ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-field-diagnostics-v1.js').read_text()
css = (ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.33.0.css').read_text()
manifest = json.loads((ROOT/'release-manifest-v0.33.0.json').read_text())
record = json.loads((ROOT/'registry/workspace-product-record-v0.33.0.json').read_text())

check('Version: 0.33.0' in main and "define('SC_WORKSPACE_VERSION', '0.33.0')" in main, 'plugin/runtime version')
check(manifest['version']=='0.33.0' and manifest['previous_version']=='0.32.0', 'manifest release lineage')
check(manifest['release_name']=='Source Capture & Research Clipping', 'release name')
check(manifest['storage_schema_version']==29 and manifest['project_schema']=='sc-workspace-project/14.0' and manifest['export_schema']=='sc-workspace-project-export/14.0', 'storage 29 / project 14.0 / export 14.0')
check(manifest['schema_migration_required'] and manifest['migration']['storage_from']==28 and manifest['migration']['storage_to']==29, 'storage 28→29 migration')
check(not manifest['migration']['project_schema_unchanged'] and manifest['migration']['project_schema_from']=='sc-workspace-project/13.0' and manifest['migration']['project_schema_to']=='sc-workspace-project/14.0', 'project schema 13.0→14.0')
check("const STORAGE_VERSION = 29" in js and "const PROJECT_SCHEMA = 'sc-workspace-project/14.0'" in js and 'function migrateV28(raw)' in js, 'browser migration runtime')
check(manifest['migration']['preserves_existing_notebooks'] and manifest['migration']['upgrades_notebook_blocks_to_v2'] and manifest['migration']['initializes_source_capture_inbox'], 'Source Capture migration boundaries')
check(manifest['notebook_workspace_schema']=='sc-workspace-notebook-workspace/2.0' and manifest['notebook_schema']=='sc-workspace-notebook/2.0' and manifest['notebook_block_schema']=='sc-workspace-notebook-block/2.0', 'Research Notebook v2 schemas')
check(manifest['notebook_export_schema']=='sc-workspace-notebook-export/2.0' and 'blockFromCapture' in notebook and 'citationLine' in notebook and 'exportNotebook' in notebook, 'Notebook capture context and portable export')
sc = manifest['source_capture']
check(sc['schema']=='sc-workspace-source-capture-inbox/1.0' and sc['request_schema']=='sc-workspace-notebook-capture-request/1.0' and sc['provenance_schema']=='sc-workspace-source-capture/1.0' and sc['bibliographic_context_schema']=='sc-workspace-bibliographic-context/1.0', 'Source Capture schemas')
check(sc['source_surfaces']==['manual','knowledge-library','research-librarian','external-web','document','workspace-object','other'], 'Source Capture surfaces')
check(sc['capture_types']==['source','excerpt','note','question','claim','reference','attachment'] and sc['max_inbox_requests']==100, 'Source Capture types and inbox limit')
check(sc['same_origin_session_staging'] and sc['same_origin_postmessage'] and sc['portable_json_capture_request'], 'same-origin and portable capture adapters')
check(sc['incoming_capture_requires_explicit_save'] and sc['project_destination_required_before_commit'] and not sc['research_content_in_handoff_url'], 'explicit capture commit boundary')
check(not sc['automatic_remote_fetch'] and not sc['automatic_page_scraping'] and not sc['automatic_metadata_inference'] and not sc['automatic_ai'] and not sc['automatic_upload'], 'no automatic fetch/scrape/inference/AI/upload')
check("const MESSAGE_TYPE='sc-workspace-notebook-capture'" in capture and "const SESSION_KEY='sc_workspace_notebook_capture_v1'" in capture and 'stageAndOpen' in capture and 'fromPageSelection' in capture, 'Source Capture producer helper')
check("'/source-capture-contract'" in php and 'public function source_capture_contract()' in php and '/wp-json/sc-workspace/v1/source-capture-contract' in manifest['rest_routes'], 'Source Capture REST contract')
check('data-scw-notebook-capture-form' in php and 'Save capture to active section' in php and 'data-scw-notebook-capture-inbox' in php and 'data-scw-notebook-capture-import' in php, 'Source Capture application surface')
check('sc_workspace_source_capture_adapter_script_url' in main and 'sc-workspace-source-capture-v1.js' in main, 'public Source Capture adapter helper URL')
check("'sc-workspace-source-capture-v1'" in php and "'sc-workspace-research-notebook-v2'" in php, 'Source Capture and Notebook v2 asset dependency')
check(manifest['research_notebook']['promotion_explicit'] and manifest['research_notebook']['promotion_preserves_original_block'] and not manifest['research_notebook']['automatic_promotion'], 'explicit Notebook promotion retained')
check(not manifest['research_notebook']['automatic_ai'] and not manifest['research_notebook']['ai_required'] and not manifest['governance']['notebook_automatic_ai'], 'Notebook does not require or auto-run AI')
check(manifest['migration']['preserves_account_persistence'] and manifest['migration']['preserves_cross_device_sync'] and manifest['migration']['preserves_version_history'] and manifest['migration']['preserves_safe_actions'] and manifest['migration']['preserves_reconciliation_receipts'] and manifest['migration']['preserves_project_lifecycle'], 'migration preserves governance and recovery state')
check(manifest['canonical_library_path']=='/knowledge-libraries/' and '/knowledge-libraries/' in php, 'canonical Knowledge Library route')
check(record['public_version']=='0.33.0' and record['previous_version']=='0.32.0', 'registry record lineage')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0330'" in reg and "PENDING_KEY = 'sc_workspace_registry_pending_v0330'" in reg and 'LEGACY_PENDING_KEY_V0320' in reg and 'LEGACY_PENDING_KEY_V0320' in php, 'registry pending/backup lineage')
check((ROOT/'history/release-manifest-v0.32.0.json').exists() and (ROOT/'history/workspace-product-record-v0.32.0.json').exists(), 'v0.32.0 history preserved')
check(not manifest['field_diagnostics']['automatic_telemetry'] and not manifest['field_diagnostics']['automatic_submission'] and 'userReviewedBeforeExport' in field_helper, 'v0.31 Field Diagnostics retained')
check(':focus-visible' in css and 'prefers-reduced-motion:reduce' in css and 'forced-colors:active' in css, 'accessibility hardening retained')
for f in (
    'sc-workspace-bibliographic-context-v1.schema.json',
    'sc-workspace-source-capture-v1.schema.json',
    'sc-workspace-notebook-capture-request-v1.schema.json',
    'sc-workspace-source-capture-inbox-v1.schema.json',
    'sc-workspace-notebook-block-v2.schema.json',
    'sc-workspace-notebook-v2.schema.json',
    'sc-workspace-notebook-workspace-v2.schema.json',
    'sc-workspace-project-v14.schema.json',
):
    json.loads((ROOT/'schemas'/f).read_text())
check(True, 'Source Capture / Notebook v2 schema JSON')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.33.0 — Source Capture & Research Clipping')
