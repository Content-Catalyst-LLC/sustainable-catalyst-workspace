#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def check(c,m):
 if not c: errors.append(m)
main=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'; php=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'; platform=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-platform.php'; js=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.6.1.js'; css=ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.6.1.css'
required=(main,php,platform,js,css,ROOT/'schemas/sc-workspace-project-v5.schema.json',ROOT/'schemas/sc-workspace-decision-v1.schema.json',ROOT/'schemas/sc-workspace-analysis-v1.schema.json',ROOT/'schemas/sc-workspace-identity-v1.schema.json',ROOT/'schemas/sc-workspace-research-v1.schema.json',ROOT/'schemas/sc-workspace-object-v1.schema.json',ROOT/'release-manifest-v0.6.1.json',ROOT/'registry/workspace-product-record-v0.6.1.json',ROOT/'docs/DEDICATED_WORKSPACE_PAGE_PLATFORM_CONVERSION_V061.md')
for p in required: check(p.exists(),f'missing required file: {p.relative_to(ROOT)}')
if main.exists():
 t=main.read_text(); check('Version: 0.6.1' in t,'plugin header version mismatch'); check('class-sc-workspace-platform.php' in t,'platform controller not loaded')
if js.exists():
 t=js.read_text()
 for token in ("const STORAGE_VERSION = 7","const PROJECT_SCHEMA = 'sc-workspace-project/5.0'","const DECISION_SCHEMA = 'sc-workspace-decision/1.0'",'function migrateV6(raw)','cloudSync: false','serverProjectStorage: false'): check(token in t,f'JS contract missing: {token}')
if php.exists():
 t=php.read_text()
 for token in ("add_shortcode('sc_workspace_platform'","'/platform-contract'",'Research. Analyze. Decide. Carry the work forward.','FREE PUBLIC ACCESS','SC_Workspace_Platform::canonical_url()'): check(token in t,f'PHP/UI contract missing: {token}')
if platform.exists():
 t=platform.read_text()
 for token in ('perform_conversion','perform_restore','sc_workspace_platform_backup_v061_',"get_page_by_path('platform'",'[sc_workspace_platform]','maybe_redirect_legacy_workspace_route'):
  check(token in t,f'Platform conversion contract missing: {token}')
 check("'post_title' => 'Workspace'" in t,'conversion title update missing'); check("'post_content' => '[sc_workspace_platform]'" in t,'conversion shortcode update missing'); check("'post_name' =>" not in t,'conversion must not rewrite page slug'); check("'post_parent' =>" not in t,'conversion must not rewrite page parent')
try:
 m=json.loads((ROOT/'release-manifest-v0.6.1.json').read_text()); check(m['version']=='0.6.1','manifest version'); check(m['previous_version']=='0.6.0','previous version'); check(m['release_name']=='Dedicated Workspace Page & Platform Conversion','release name'); check(m['storage_schema_version']==7,'storage schema changed unexpectedly'); check(m['project_schema']=='sc-workspace-project/5.0','project schema changed unexpectedly'); check(m['platform_conversion']['automatic'] is False,'automatic conversion must be false'); check(m['platform_conversion']['rollback_snapshot'] is True,'rollback snapshot missing'); check(m['cloud_sync'] is False,'cloud sync')
except Exception as e: errors.append(f'manifest parse failed: {e}')
try:
 r=json.loads((ROOT/'registry/workspace-product-record-v0.6.1.json').read_text()); check(r['public_version']=='0.6.1','registry version'); check(r['previous_version']=='0.6.0','registry previous'); check(r['family']=='commercial','registry family'); check(r['product_url']=='/platform/','registry product URL')
except Exception as e: errors.append(f'registry parse failed: {e}')
if errors:
 print('VALIDATION FAILED'); [print(' - '+e) for e in errors]; sys.exit(1)
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.6.1 — Dedicated Workspace Page & Platform Conversion')
