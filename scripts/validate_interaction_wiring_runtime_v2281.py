from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
wp=ROOT/'wordpress/sustainable-catalyst-workspace'
js=(wp/'assets/js/workspace-v2.28.1.js').read_text()
bootstrap=(wp/'assets/js/sc-workspace-interaction-bootstrap-v2281.js').read_text()
php=(wp/'includes/class-sc-workspace.php').read_text()
plugin=(wp/'sustainable-catalyst-workspace.php').read_text()
backend=(ROOT/'backend/app/config.py').read_text()
deployer=(ROOT/'backend/deploy_workspace_backend_v2_28_1_vps.sh').read_text()
checks={
 'plugin version': 'Version: 2.28.1' in plugin and "SC_WORKSPACE_VERSION', '2.28.1" in plugin,
 'asset alignment': 'workspace-v2.28.1.js' in php and 'workspace-v2.28.1.css' in php and 'sc-workspace-interaction-bootstrap-v2281.js' in php,
 'client identity': "const WORKSPACE_RELEASE = '2.28.1';" in js,
 'runtime diagnostics': 'SCWorkspaceInteractionRuntime' in js and 'interactionRuntime.audit' in js,
 'delegated fallback': "document.addEventListener('click'" in bootstrap and "[data-scw-workspace-view]" in bootstrap and "[data-scw-new-project]" in bootstrap,
 'null safe core': "bindControl('[data-scw-new-project]'" in js and "bindControl('[data-scw-delete]'" in js,
 'no brittle root click binding': not re.search(r"root\.querySelector\('[^']+'\)\.addEventListener\('click'",js),
 'ready marker': "root.dataset.scwRuntimeReady = '1'" in js,
 'backend identity': 'service_version: str = "2.28.1"' in backend,
 'deployer identity': "d['version']=='2.28.1'" in deployer and 'v2.28.1' in deployer,
}
failed=[name for name,ok in checks.items() if not ok]
for name,ok in checks.items(): print(('PASS' if ok else 'FAIL')+': '+name)
if failed: raise SystemExit('FAILED: '+', '.join(failed))
print('PASS: Workspace v2.28.1 interaction wiring/runtime repair contract')
