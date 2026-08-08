#!/usr/bin/env python3
from pathlib import Path
import json, re, sys
root = Path(__file__).resolve().parents[1]
errors=[]
def ok(cond,msg):
    if not cond: errors.append(msg)
main=root/'wordpress'/'sustainable-catalyst-workspace'/'sustainable-catalyst-workspace.php'
reg=root/'wordpress'/'sustainable-catalyst-workspace'/'includes'/'class-sc-workspace-registry.php'
ui=root/'wordpress'/'sustainable-catalyst-workspace'/'includes'/'class-sc-workspace.php'
js=root/'wordpress'/'sustainable-catalyst-workspace'/'assets'/'js'/'workspace-v0.1.0.js'
css=root/'wordpress'/'sustainable-catalyst-workspace'/'assets'/'css'/'workspace-v0.1.0.css'
for p in [main,reg,ui,js,css,root/'release-manifest-v0.1.0.json',root/'registry'/'workspace-product-record-v0.1.0.json']:
    ok(p.exists(),f'missing: {p.relative_to(root)}')
if main.exists():
    t=main.read_text(); ok('Version: 0.1.0' in t,'plugin version mismatch'); ok('register_activation_hook' in t,'activation hook missing')
if reg.exists():
    t=reg.read_text();
    for token in ["'canonical_id' => self::CANONICAL_ID","'family' => 'commercial'","'console_screen' => 'commercial'","'display_order' => 400","'commercial' => '1'","'public_interest' => '1'","'lifecycle_state' => 'experimental'","BACKUP_KEY"]: ok(token in t,f'registry token missing: {token}')
if ui.exists():
    t=ui.read_text();
    for token in ["add_shortcode('sc_workspace'","add_shortcode('sc_workspace_entry'","sc-workspace/v1","account_required' => false","server_project_storage' => false"]: ok(token in t,f'workspace contract missing: {token}')
if js.exists():
    t=js.read_text(); ok('localStorage' in t,'browser-local state missing'); ok('MAX_RECENT = 5' in t,'recent tool bound missing')
manifest=json.loads((root/'release-manifest-v0.1.0.json').read_text())
ok(manifest['version']=='0.1.0','manifest version mismatch'); ok(manifest['access_model']=='free-public','access model mismatch'); ok(manifest['registry']['family']=='commercial','manifest registry family mismatch')
record=json.loads((root/'registry'/'workspace-product-record-v0.1.0.json').read_text())
ok(record['canonical_id']=='sustainable-catalyst-workspace','canonical id mismatch'); ok(record['family']=='commercial','record family mismatch'); ok(record['public_version']=='0.1.0','public version mismatch')
if errors:
    print('VALIDATION FAILED')
    for e in errors: print('FAIL -',e)
    sys.exit(1)
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.1.0')
print('PASS - canonical product identity')
print('PASS - Commercial Release registry placement')
print('PASS - free public access boundary')
print('PASS - browser-local session foundation')
print('PASS - shortcode and REST contracts')
