from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.66.1.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.66.1.json').read_text())
MAINP=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
MAIN=MAINP.read_text(); B=MAINP.read_bytes(); W=B[:8192].decode('utf-8',errors='replace')
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
BETA=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-ii-ui-v1.js').read_text()
HARD=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-import-export-compatibility-v1.js').read_text()
def check(ok,label):
 if not ok: raise SystemExit('FAIL - '+label)
check('Version: 0.66.1' in MAIN and "SC_WORKSPACE_VERSION', '0.66.1" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.66.1','0.66.0','WordPress Plugin Header Metadata Recovery'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'canonical schemas stable')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.66.1'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
 m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',W,re.I|re.M); check(bool(m) and m.group(1).strip()==expected,'8KB header '+label)
check(B.find(b'Version:')<512 and B.find(b'Requires PHP:')<512 and B.find(b'Description:')<1024,'compact plugin header')
check('workspace-v0.66.0.js' in PHP and 'workspace-v0.66.0.css' in PHP,'v0.66 cumulative assets retained')
check("expectedVersion:'0.66.1'" in BETA and "root.dataset.version==='0.66.1'" in BETA,'beta current version gate')
check("workspaceVersion:'0.66.1'" in HARD,'compatibility report current version')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0661'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0661'" in REGPHP and 'LEGACY_PENDING_KEY_V0660' in REGPHP,'registry recovery lineage')
check(REG['public_version']=='0.66.1' and REG['previous_version']=='0.66.0','registry record')
check((ROOT/'history/release-manifest-v0.66.0.json').exists() and (ROOT/'history/workspace-product-record-v0.66.0.json').exists(),'v0.66 history retained')
print('PASS - v0.66.1 release validator')
