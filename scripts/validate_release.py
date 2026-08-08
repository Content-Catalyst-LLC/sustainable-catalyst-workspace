#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def check(c,m):
    if not c: errors.append(m)
main=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
php=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
platform=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-platform.php'
js=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.7.0.js'
css=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.7.0.css'
required=(main,php,platform,js,css,ROOT/'schemas/sc-workspace-project-v6.schema.json',ROOT/'schemas/sc-workspace-canvas-v1.schema.json',ROOT/'schemas/sc-workspace-decision-v1.schema.json',ROOT/'schemas/sc-workspace-analysis-v1.schema.json',ROOT/'schemas/sc-workspace-identity-v1.schema.json',ROOT/'schemas/sc-workspace-research-v1.schema.json',ROOT/'schemas/sc-workspace-object-v1.schema.json',ROOT/'release-manifest-v0.7.0.json',ROOT/'registry/workspace-product-record-v0.7.0.json',ROOT/'docs/CANVAS_STRUCTURED_THINKING_V070.md')
for p in required: check(p.exists(),f'missing required file: {p.relative_to(ROOT)}')
if main.exists():
    t=main.read_text(); check('Version: 0.7.0' in t,'plugin header version mismatch'); check("define('SC_WORKSPACE_VERSION', '0.7.0')" in t,'runtime version mismatch')
if js.exists():
    t=js.read_text()
    for token in ("const STORAGE_VERSION = 8","const PROJECT_SCHEMA = 'sc-workspace-project/6.0'","const CANVAS_SCHEMA = 'sc-workspace-canvas/1.0'",'function migrateV7(raw)','function renderCanvas(project)','function cleanCanvasReferences','const boardMap = new Map()',"objectTemplate('document',`${board.title} — Canvas synthesis`)","target.searchParams.set('sc_workspace_canvas', activeBoard.id)",'cloudSync: false','serverProjectStorage: false'):
        check(token in t,f'JS contract missing: {token}')
if php.exists():
    t=php.read_text()
    for token in ("'/canvas-contract'",'CANVAS &amp; STRUCTURED THINKING','Structured canvas','Typed relationships','Capture synthesis',"'canvas_schema' => 'sc-workspace-canvas/1.0'","'storage_schema_version' => 8","'project_schema' => 'sc-workspace-project/6.0'"):
        check(token in t,f'PHP/UI contract missing: {token}')
if platform.exists():
    t=platform.read_text()
    for token in ('perform_conversion','perform_restore','sc_workspace_platform_backup_v061_',"get_page_by_path('platform'",'[sc_workspace_platform]','maybe_redirect_legacy_workspace_route'):
        check(token in t,f'Platform conversion regression: {token}')
    check("'post_name' =>" not in t,'conversion must not rewrite page slug'); check("'post_parent' =>" not in t,'conversion must not rewrite page parent')
try:
    c=json.loads((ROOT/'schemas/sc-workspace-canvas-v1.schema.json').read_text()); check(c['properties']['schema']['const']=='sc-workspace-canvas/1.0','canvas schema id'); check(c['properties']['nodes']['maxItems']==500,'canvas node limit'); check(c['properties']['edges']['maxItems']==1000,'canvas edge limit')
    p=json.loads((ROOT/'schemas/sc-workspace-project-v6.schema.json').read_text()); check(p['properties']['schema']['const']=='sc-workspace-project/6.0','project schema'); check(p['properties']['canvas']['$ref']=='sc-workspace-canvas-v1.schema.json','project canvas ref')
except Exception as e: errors.append(f'schema parse failed: {e}')
try:
    m=json.loads((ROOT/'release-manifest-v0.7.0.json').read_text()); check(m['version']=='0.7.0','manifest version'); check(m['previous_version']=='0.6.1','previous version'); check(m['release_name']=='Canvas & Structured Thinking','release name'); check(m['storage_schema_version']==8,'storage schema'); check(m['project_schema']=='sc-workspace-project/6.0','project schema'); check(m['canvas_schema']=='sc-workspace-canvas/1.0','canvas schema'); check(m['handoff_schema']=='sc-workspace-handoff/1.5','handoff schema'); check(m['cloud_sync'] is False,'cloud sync'); check(m['platform_conversion']['automatic'] is False,'automatic conversion must remain false')
except Exception as e: errors.append(f'manifest parse failed: {e}')
try:
    r=json.loads((ROOT/'registry/workspace-product-record-v0.7.0.json').read_text()); check(r['public_version']=='0.7.0','registry version'); check(r['previous_version']=='0.6.1','registry previous'); check(r['family']=='commercial','registry family'); check(r['product_url']=='/platform/','registry product URL')
except Exception as e: errors.append(f'registry parse failed: {e}')
if errors:
    print('VALIDATION FAILED'); [print(' - '+e) for e in errors]; sys.exit(1)
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.7.0 — Canvas & Structured Thinking')
