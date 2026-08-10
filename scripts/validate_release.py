import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.56.0.json').read_text());REG=json.loads((ROOT/'registry/workspace-product-record-v0.56.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text();PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text();REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text();HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-automation-v1.js').read_text();UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-research-automation-ui-v1.js').read_text();CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.56.0.css').read_text()
def check(ok,msg):
 if not ok: raise SystemExit('FAIL - '+msg)
 print('PASS - '+msg)
check('Version: 0.56.0' in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.56.0','0.55.0','Research Automation Framework'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0','schema stable')
check('/wp-json/sc-workspace/v1/research-automation-contract' in MAN['rest_routes'],'automation REST contract')
check(MAN['research_automation']['manual_execution_only'] and not MAN['research_automation']['background_execution'],'manual execution boundary')
check(not MAN['research_automation']['automatic_network_request'] and not MAN['research_automation']['automatic_canonical_mutation'],'no background network or canonical mutation')
check('sc-workspace-research-automation-v1.js' in PHP and 'sc-workspace-research-automation-ui-v1.js' in PHP,'automation assets enqueued')
check('Run due routines' in PHP and 'Automation run receipts' in PHP,'automation UI')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0560'" in REGPHP and 'LEGACY_PENDING_KEY_V0550' in REGPHP,'registry lineage')
check(REG['public_version']=='0.56.0' and REG['previous_version']=='0.55.0','registry record')
check('border-top:4px solid #000' in CSS,'4px editorial automation header')
check((ROOT/'history/release-manifest-v0.55.0.json').exists(),'v0.55 history retained')
print('PASS - v0.56.0 release validator')
