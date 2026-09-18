from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
plugin=ROOT/'wordpress/sustainable-catalyst-workspace'
main=(plugin/'sustainable-catalyst-workspace.php').read_text()
cls=(plugin/'includes/class-sc-workspace.php').read_text()
js=(plugin/'assets/js/workspace-v2.24.1.js').read_text()
css=(plugin/'assets/css/workspace-v2.24.1.css').read_text()
assert 'Version: 2.24.1' in main
assert "SC_WORKSPACE_VERSION', '2.24.1'" in main
assert 'workspace-v2.24.1.js' in cls and 'workspace-v2.24.1.css' in cls
assert len(js) > 850000, len(js)
assert len(css) > 340000, len(css)
assert 'function setWorkspaceView' in js
assert 'root.querySelectorAll(\'[data-scw-workspace-section]\')' in js
assert 'SCWorkspaceBackendAuthority' in js
assert 'SCWorkspaceDecisionAnalysis' in js
assert 'SCWorkspaceReliabilityAnalysis' in js
assert 'SCWorkspaceInterfaceShell' in js
assert 'data-scw-primary-analyze' in cls
assert '>Analyze</button>' in cls
assert 'data-scw-deployment-expected-script="workspace-v2.24.1.js"' in cls
assert 'data-scw-deployment-expected-style="workspace-v2.24.1.css"' in cls
assert '[data-scw-workspace-section][hidden]' in css
assert 'data-scw-workspace-section="home" data-scw-connected-knowledge hidden' in cls
assert 'data-scw-workspace-section="home" data-scw-connected-intelligence hidden' in cls
assert 'data-scw-workspace-section="review" data-scw-institutional-scale hidden' in cls
assert "service_version: str = \"2.24.1\"" in (ROOT/'backend/app/config.py').read_text()
deployer=(ROOT/'backend/deploy_workspace_backend_v2_24_1_vps.sh').read_text()
assert re.search(r"d\['version'\]\s*==\s*'2\.24\.1'", deployer)
print('PASS - Workspace v2.24.1 interface shell + version alignment contract')
