#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.37.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.37.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.37.0.js').read_text()
NB=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v6.js').read_text()
ADAPTER=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-notebook-assistance-adapter-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.37.0.css').read_text()

def check(ok,label):
    if not ok: raise SystemExit(f'FAIL - {label}')
    print(f'PASS - {label}')

check('Version: 0.37.0' in MAIN and "SC_WORKSPACE_VERSION', '0.37.0" in MAIN,'plugin/runtime version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.37.0','0.36.0','Grounded Notebook Assistance'),'manifest release lineage')
check((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema'])==(33,'sc-workspace-project/18.0','sc-workspace-project-export/18.0'),'storage 33 / project 18.0 / export 18.0')
check((MAN['migration']['storage_from'],MAN['migration']['storage_to'])==(32,33),'storage 32→33 migration')
check((MAN['migration']['project_schema_from'],MAN['migration']['project_schema_to'])==('sc-workspace-project/17.0','sc-workspace-project/18.0'),'project schema 17.0→18.0')
check('function migrateV32(raw)' in JS and 'if (raw.schemaVersion === 32) return migrateV32(raw);' in JS,'browser migration runtime')
check((MAN['notebook_workspace_schema'],MAN['notebook_schema'],MAN['notebook_block_schema'],MAN['notebook_export_schema'])==('sc-workspace-notebook-workspace/6.0','sc-workspace-notebook/3.0','sc-workspace-notebook-block/3.0','sc-workspace-notebook-export/6.0'),'Notebook v6 container schemas')
check((MAN['notebook_assistance_schema'],MAN['notebook_assistance_request_export_schema'],MAN['notebook_assistance_response_export_schema'])==('sc-workspace-notebook-assistance/1.0','sc-workspace-notebook-assistance-request-export/1.0','sc-workspace-notebook-assistance-response-export/1.0'),'Grounded Assistance schemas')
rn=MAN['research_notebook']; g=MAN['governance']
check(rn['assistance_requires_explicit_selection'] and rn['assistance_question_required'],'explicit grounded question selection')
check(rn['assistance_response_requires_citations'] and rn['assistance_citation_markers_resolve_to_selected_material'],'citations required against selected material')
check(rn['assistance_invalid_citation_markers_rejected'] and rn['assistance_output_is_reviewable_draft'],'invalid citations rejected / answer remains draft')
check(rn['provider_neutral_assistance_transport'] and rn['portable_assistance_request_export'] and rn['portable_assistance_response_export'],'provider-neutral portable assistance transport')
check(rn['assistance_can_materialize_document_explicitly'] and not rn['assistance_automatic_materialization'],'explicit Document materialization only')
check(all(x in NB for x in ('prepareAssistance','assistancePrompt','validateAssistanceResponse','applyAssistanceResponse','exportAssistanceRequest','exportAssistanceResponse','assistancesForRef')),'assistance helper runtime')
check(all(x in JS for x in ('renderNotebookAssistance(project)','helper.prepareAssistance','helper.applyAssistanceResponse','Copy grounded prompt','Create Document')),'assistance application runtime')
check(all(x in PHP for x in ('data-scw-notebook-assistance-form','data-scw-notebook-assistance-material','data-scw-notebook-assistance-list','Prepare grounded question')),'assistance application surface')
check(all(x in ADAPTER for x in ('sc_workspace_notebook_assistance_request_v1','sc_workspace_notebook_assistance_response_v1','citationsLimitedToSelectedMaterial','postMessage')),'assistance adapter contract')
check("'schema' => 'sc-workspace-project-contract/18.0'" in PHP and "'export_schema' => 'sc-workspace-project-export/18.0'" in PHP,'Project REST contract v18')
check("array('sc-workspace-project/18.0','sc-workspace-project/17.0','sc-workspace-project/16.0'" in PHP,'account persistence accepts Project v18 + legacy window')
check("'notebook_workspace_schema' => 'sc-workspace-notebook-workspace/6.0'" in PHP and "'notebook_assistance_schema' => 'sc-workspace-notebook-assistance/1.0'" in PHP,'Notebook REST assistance contract')
check("'grounded_assistance_citations_required' => true" in PHP and "'grounded_assistance_automatic_submission' => false" in PHP,'REST grounded-assistance boundaries')
check(g['notebook_assistance_explicit_selection_required'] and g['notebook_assistance_citations_required'],'selection/citation governance')
check(not g['notebook_assistance_automatic_submission'] and not g['automatic_ai_submission'],'no automatic assistance submission')
check(not g['notebook_assistance_automatic_acceptance'] and not g['notebook_assistance_automatic_source_mutation'],'no automatic answer acceptance/source mutation')
check(not g['notebook_assistance_automatic_document_materialization'] and g['notebook_assistance_response_is_reviewable_draft'],'draft-first materialization boundary')
check(g['notebook_assistance_citations_limited_to_selected_material'] and g['notebook_assistance_invalid_citations_rejected'],'selected-material citation enforcement')
check(MAN['migration']['preserves_notebook_syntheses'] and MAN['migration']['preserves_notebook_promotions'] and MAN['migration']['preserves_notebook_links'] and MAN['migration']['preserves_notebook_collections'],'v0.34–v0.36 notebook state preserved')
check(MAN['migration']['preserves_source_capture'] and MAN['migration']['preserves_existing_notebooks'] and MAN['migration']['preserves_canonical_objects'],'source capture/notebooks/canonical objects preserved')
check(MAN['canonical_library_path']=='/knowledge-libraries/' and '/knowledge-libraries/' in PHP,'canonical Knowledge Library route')
check((REG['public_version'],REG['previous_version'])==('0.37.0','0.36.0'),'registry release lineage')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0370'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0370'" in REGPHP and 'LEGACY_PENDING_KEY_V0360' in REGPHP,'registry pending/backup lineage')
check('LEGACY_PENDING_KEY_V0360' in PHP and 'LEGACY_PENDING_KEY_V0350' in PHP,'registry retry lineage')
check((ROOT/'history/release-manifest-v0.36.0.json').exists() and (ROOT/'history/workspace-product-record-v0.36.0.json').exists(),'v0.36.0 history preserved')
for name in (
 'sc-workspace-notebook-assistance-v1.schema.json','sc-workspace-notebook-assistance-request-export-v1.schema.json',
 'sc-workspace-notebook-assistance-response-export-v1.schema.json','sc-workspace-notebook-workspace-v6.schema.json',
 'sc-workspace-notebook-export-v6.schema.json','sc-workspace-project-v18.schema.json'):
    json.loads((ROOT/'schemas'/name).read_text())
check(True,'Grounded Assistance schema JSON')
check(all(x in CSS for x in ('.scw-notebook-assistance', '.scw-notebook-assistance-card', '.scw-notebook-assistance-material')),'Grounded Assistance visual layer')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.37.0 — Grounded Notebook Assistance')
