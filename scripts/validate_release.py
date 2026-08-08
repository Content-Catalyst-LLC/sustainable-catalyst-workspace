#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def check(c,m):
    if not c: errors.append(m)
plugin=ROOT/'wordpress/sustainable-catalyst-workspace'
required=[plugin/'sustainable-catalyst-workspace.php',plugin/'includes/class-sc-workspace.php',plugin/'includes/class-sc-workspace-registry.php',plugin/'includes/class-sc-workspace-platform.php',plugin/'assets/js/workspace-v0.8.3.js',plugin/'assets/js/sc-workspace-return-adapter-v1.js',plugin/'assets/css/workspace-v0.8.3.css',ROOT/'release-manifest-v0.8.3.json',ROOT/'registry/workspace-product-record-v0.8.3.json',ROOT/'docs/ADVISORY_VISUAL_INTEGRATION_WORKSPACE_EDITORIAL_SHELL_V083.md']
for p in required: check(p.exists(),f'missing required file: {p.relative_to(ROOT)}')
main=(plugin/'sustainable-catalyst-workspace.php').read_text(); check('Version: 0.8.3' in main,'plugin version'); check("define('SC_WORKSPACE_VERSION', '0.8.3')" in main,'runtime version')
php=(plugin/'includes/class-sc-workspace.php').read_text(); css=(plugin/'assets/css/workspace-v0.8.3.css').read_text(); js=(plugin/'assets/js/workspace-v0.8.3.js').read_text(); platform=(plugin/'includes/class-sc-workspace-platform.php').read_text()
for token in ('scw-platform-hero-grid','ILLUSTRATIVE WORKSPACE','ONE PERSONAL WORKSPACE','WORKSPACE PATHWAYS','PERSONAL CAPABILITY','WORKSPACE APPLICATION','scw-editorial-closing','data-scw-project-mode="overview"',"'recommended_navigation_label' => 'Workspace'", "'public_experience' => 'advisory-aligned-editorial'"): check(token in php,f'public/editorial UI missing: {token}')
for token in ('v0.8.3 — Advisory Visual Integration & Workspace Editorial Shell','--scw-warm:#f7f3ea','--scw-dark:#0d0d0d','--scw-accent:#ff0000','.scw-platform-application-editorial','.scw-pathway-list','.scw-capability-dark'): check(token in css,f'editorial CSS missing: {token}')
for token in ('function setProjectMode(mode)',"root.classList.add('scw-mode-enabled')"): check(token in js,f'JS mode navigation missing: {token}')
for token in ("NAV_BACKUP_KEY = 'sc_workspace_navigation_backup_v082'",'relabel_navigation_items','restore_navigation_items'): check(token in platform,f'navigation governance missing: {token}')
try:
    m=json.loads((ROOT/'release-manifest-v0.8.3.json').read_text()); check(m['version']=='0.8.3','manifest version'); check(m['previous_version']=='0.8.2','manifest previous'); check(m['release_name']=='Advisory Visual Integration & Workspace Editorial Shell','release name'); check(m['storage_schema_version']==9,'storage unchanged'); check(m['project_schema']=='sc-workspace-project/7.0','project unchanged'); check(m['cloud_sync'] is False,'cloud sync')
except Exception as e: errors.append(f'manifest parse failed: {e}')
try:
    r=json.loads((ROOT/'registry/workspace-product-record-v0.8.3.json').read_text()); check(r['public_version']=='0.8.3','registry version'); check(r['previous_version']=='0.8.2','registry previous'); check(r['family']=='commercial','registry family'); check(r['product_url']=='/platform/','canonical product route')
except Exception as e: errors.append(f'registry parse failed: {e}')
if errors:
    print('VALIDATION FAILED'); [print(' - '+e) for e in errors]; sys.exit(1)
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.8.3 — Advisory Visual Integration & Workspace Editorial Shell')
