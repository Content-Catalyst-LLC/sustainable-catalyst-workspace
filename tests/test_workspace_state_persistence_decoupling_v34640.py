from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'wordpress/sustainable-catalyst-workspace'
PLUGIN=P/'sustainable-catalyst-workspace.php';WORKSPACE=P/'includes/class-sc-workspace.php';DEPLOY=P/'includes/class-sc-workspace-deployment.php';CONFIG=ROOT/'backend/app/config.py'
STATE=ROOT/'app/state/workspace-state-store-v34640.js';PERSIST=ROOT/'app/state/workspace-persistence-runtime-v34640.js';KERNEL=ROOT/'app/core/workspace-application-kernel-v34640.js';SHELL=P/'assets/js/workspace-v3.46.4.0.js';COMPAT=P/'assets/js/sc-workspace-local-project-compat-v34640.js'
def test_release(): assert 'Version: 3.46.4.0' in PLUGIN.read_text() and 'service_version: str = "3.46.4.0"' in CONFIG.read_text()
def test_state_modules(): assert 'sc-workspace-state-store/1.0' in STATE.read_text() and 'sc-workspace-persistence-runtime/1.0' in PERSIST.read_text()
def test_no_wp_core():
    for path in (STATE,PERSIST):
        t=path.read_text().lower()
        for m in ('wp_enqueue_','wp_localize_','wp-json','wp-content','wp-admin','window.scworkspaceidentity','wordpress/sustainable-catalyst-workspace'): assert m not in t
def test_verified_persistence():
    t=PERSIST.read_text(); assert 'storage.setItem(keys.current,serialized)' in t; assert 'const verified=storage.getItem(keys.current)' in t; assert 'read-after-write verification failed' in t; assert 'captureLastGoodSnapshot' in t; assert 'readLastGoodState' in t; assert 'quarantine' in t
def test_state_identity(): t=STATE.read_text(); assert 'replaceInPlace' in t and 'canonicalStateOwned:true' in t
def test_compat_delegates():
    t=COMPAT.read_text(); rb=t.split('function readState()',1)[1].split('function writeState',1)[0]; wb=t.split('function writeState',1)[1].split('function formatTime',1)[0]
    assert 'canonicalStateStore' in rb and 'localStorage' not in rb; assert 'canonicalStateStore.persist' in wb and 'localStorage' not in wb; assert 'prepareStateForPersistence' in t
def test_project_port_canonical():
    t=COMPAT.read_text(); b=t.split("schema: 'sc-workspace-compatibility-project-state-port/1.0'",1)[1].split('applicationKernel.registerProjectLifecycle',1)[0]; assert 'canonicalStateStore.current()' in b
def test_shell_load_order():
    t=SHELL.read_text(); assert 'stateStoreRuntimeUrl' in t and 'persistenceRuntimeUrl' in t; assert t.index("loadScriptAsset(persistenceRuntimeUrl") < t.index("loadCompat('v3.46.4.0-core-interaction-continuity')")
def test_kernel_services():
    t=KERNEL.read_text(); assert 'registerPersistence' in t and 'registerStateStore' in t and 'canonicalStateBoundaryDecoupled' in t
def test_deployment():
    t=DEPLOY.read_text(); assert "'state_store_runtime' => 'assets/js/sc-workspace-state-store-v34640.js'" in t; assert "'persistence_runtime' => 'assets/js/sc-workspace-persistence-runtime-v34640.js'" in t; assert '$state_persistence_boundary_ok' in t; assert "const PREVIOUS_RELEASE = '3.46.3.0';" in t
def test_no_wp_script_dependency():
    t=WORKSPACE.read_text(); m=re.search(r"wp_enqueue_script\(\s*'sc-workspace-v241',\s*SC_WORKSPACE_URL \. 'assets/js/workspace-v3\.46\.4\.0\.js',\s*(array\([\s\S]*?\)),\s*SC_WORKSPACE_VERSION,\s*true\s*\)",t); assert m and re.sub(r'\s+','',m.group(1))=='array()'
