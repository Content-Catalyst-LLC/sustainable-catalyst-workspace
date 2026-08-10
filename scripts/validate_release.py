#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.35.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.35.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.35.0.js').read_text()
NB=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-notebook-v4.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.35.0.css').read_text()

def check(ok,label):
    if not ok: raise SystemExit(f'FAIL - {label}')
    print(f'PASS - {label}')

check('Version: 0.35.0' in MAIN and "SC_WORKSPACE_VERSION', '0.35.0" in MAIN,'plugin/runtime version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.35.0','0.34.0','Notebook-to-Workspace Intelligence'),'manifest release lineage')
check((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema'])==(31,'sc-workspace-project/16.0','sc-workspace-project-export/16.0'),'storage 31 / project 16.0 / export 16.0')
check((MAN['migration']['storage_from'],MAN['migration']['storage_to'])==(30,31),'storage 30→31 migration')
check((MAN['migration']['project_schema_from'],MAN['migration']['project_schema_to'])==('sc-workspace-project/15.0','sc-workspace-project/16.0'),'project schema 15.0→16.0')
check('function migrateV30(raw)' in JS and 'if (raw.schemaVersion === 30) return migrateV30(raw);' in JS,'browser migration runtime')
check((MAN['notebook_workspace_schema'],MAN['notebook_schema'],MAN['notebook_block_schema'],MAN['notebook_export_schema'],MAN['notebook_promotion_schema'])==('sc-workspace-notebook-workspace/4.0','sc-workspace-notebook/3.0','sc-workspace-notebook-block/3.0','sc-workspace-notebook-export/4.0','sc-workspace-notebook-promotion/1.0'),'Notebook promotion schemas')
check(MAN['research_notebook']['promotion_targets']==['source','evidence','dataset','analysis','decision','document','canvas'],'seven explicit promotion destinations')
check(MAN['research_notebook']['promotion_requires_explicit_destination'] and MAN['research_notebook']['multiple_derivatives_per_block'],'explicit destination / multiple derivatives')
check(MAN['research_notebook']['promotion_lineage_visible'] and MAN['research_notebook']['promotion_ledger_project_bound'],'visible project-bound promotion ledger')
check(not MAN['research_notebook']['automatic_promotion'] and not MAN['governance']['notebook_automatic_promotion'],'no automatic notebook promotion')
check(not MAN['governance']['notebook_promotion_hidden_classification'] and not MAN['governance']['notebook_promotion_ai_required'],'no hidden classification / AI requirement')
check(MAN['governance']['notebook_promotion_preserves_original_material'] and not MAN['governance']['notebook_promotion_overwrites_source_block'],'original notebook material preserved')
check(all(x in NB for x in ('createPromotion','promotionRecord','promotionsForRef','promotionDestinations','suggestedPromotionType','canvasNodeType')),'promotion helper surface')
check('function promoteNotebookBlock(project, notebook, section, block, targetType)' in JS and "if(targetType==='canvas')" in JS,'object and Canvas promotion runtime')
check('renderNotebookPromotions(project)' in JS and 'data-scw-notebook-promotion-list' in PHP,'visible promotion ledger presentation')
check("'notebook_promotion_schema' => 'sc-workspace-notebook-promotion/1.0'" in PHP and "'promotion_requires_explicit_destination' => true" in PHP,'Notebook REST promotion contract')
check("'schema' => 'sc-workspace-project-contract/16.0'" in PHP and "'export_schema' => 'sc-workspace-project-export/16.0'" in PHP,'Project REST contract v16')
check("array('sc-workspace-project/16.0','sc-workspace-project/15.0'" in PHP,'account persistence accepts Project v16 + legacy window')
check(MAN['migration']['preserves_notebook_collections'] and MAN['migration']['preserves_notebook_links'] and MAN['migration']['preserves_source_capture'],'v0.33/v0.34 research state preserved')
check('/knowledge-libraries/' in PHP,'canonical Knowledge Library route')
check(':focus-visible' in CSS and 'prefers-reduced-motion:reduce' in CSS,'accessibility hardening retained')
check((REG['public_version'],REG['previous_version'])==('0.35.0','0.34.0'),'registry record lineage')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0350'" in REGPHP and 'LEGACY_PENDING_KEY_V0340' in REGPHP,'registry pending/backup lineage')
check((ROOT/'history/release-manifest-v0.34.0.json').exists() and (ROOT/'history/workspace-product-record-v0.34.0.json').exists(),'v0.34.0 history preserved')
for name in ('sc-workspace-notebook-block-v3.schema.json','sc-workspace-notebook-v3.schema.json','sc-workspace-notebook-promotion-v1.schema.json','sc-workspace-notebook-workspace-v4.schema.json','sc-workspace-notebook-export-v4.schema.json','sc-workspace-project-v16.schema.json'):
    json.loads((ROOT/'schemas'/name).read_text())
check(True,'Notebook-to-Workspace schema JSON')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.35.0 — Notebook-to-Workspace Intelligence')
