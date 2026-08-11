#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.58.0.json').read_text());REG=json.loads((ROOT/'registry/workspace-product-record-v0.58.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text();HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-scale-performance-v1.js').read_text();UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-scale-performance-ui-v1.js').read_text();APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.58.0.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.58.0.css').read_text()
def check(ok,label):
 if not ok: raise SystemExit('FAIL - '+label)
 print('PASS - '+label)
check('Version: 0.58.0' in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.58.0','0.57.0','Scale, Performance & Large-Project Hardening'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and not MAN['scale_performance']['schema_migration'],'schema stable')
check('/wp-json/sc-workspace/v1/scale-performance-contract' in MAN['rest_routes'] and "'/scale-performance-contract'" in PHP,'scale performance REST contract')
check(MAN['scale_performance']['derived_index_cache'] and 'function deriveIntegrated' in HELP and 'deriveIntegrated(state,api)' in APP,'derived index cache')
check(MAN['scale_performance']['bounded_render_window']==120 and 'rows.slice(0,integratedRenderLimit)' in APP and 'data-scw-integrated-load-more' in PHP,'bounded result rendering')
check(MAN['scale_performance']['storage_pressure_visibility'] and 'navigator.storage' in UI,'storage pressure visibility')
check(MAN['scale_performance']['large_project_stress_fixtures'] and 'function stressFixture' in HELP,'stress fixture support')
check(MAN['scale_performance']['advisory_only'] and not MAN['scale_performance']['automatic_deletion'] and not MAN['scale_performance']['automatic_archival'] and not MAN['scale_performance']['automatic_compaction'] and not MAN['scale_performance']['canonical_mutation'],'non-destructive governance')
check('data-scw-workspace-view="performance"' in PHP and 'Run scale profile' in PHP,'Review Performance surface')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0580'" in REGPHP and 'LEGACY_PENDING_KEY_V0570' in REGPHP,'registry lineage')
check(REG['public_version']=='0.58.0' and REG['previous_version']=='0.57.0' and REG['installed_version']=='0.58.0','registry record')
check('.scw-scale-performance{border-top:4px solid #000' in CSS,'4px editorial performance header')
check((ROOT/'history/release-manifest-v0.57.0.json').exists(),'v0.57 history retained')
print('PASS - v0.58.0 release validator')
