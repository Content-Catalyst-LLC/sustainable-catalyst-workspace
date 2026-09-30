from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'wordpress/sustainable-catalyst-workspace'
PLUGIN=P/'sustainable-catalyst-workspace.php';WORKSPACE=P/'includes/class-sc-workspace.php';DEPLOYMENT=P/'includes/class-sc-workspace-deployment.php';CONFIG=ROOT/'backend/app/config.py'
CORE=(ROOT/'app/core/workspace-host-adapter-contract-v11.js',ROOT/'app/core/workspace-application-kernel-v34620.js',ROOT/'app/client/workspace-transport-v34620.js',ROOT/'app/client/workspace-auth-context-v34620.js',ROOT/'app/client/workspace-api-client-v34620.js')
WP_TRANSPORT=ROOT/'adapters/wordpress/workspace-wordpress-transport-adapter-v34620.js';WP_AUTH=ROOT/'adapters/wordpress/workspace-wordpress-auth-adapter-v34620.js';SHELL=P/'assets/js/workspace-v3.46.2.0.js';LIFECYCLE=P/'assets/js/sc-workspace-local-project-compat-v34620.js'
def test_release_identity():
 assert 'Version: 3.46.2.0' in PLUGIN.read_text();assert "define('SC_WORKSPACE_VERSION', '3.46.2.0');" in PLUGIN.read_text();assert 'service_version: str = "3.46.2.0"' in CONFIG.read_text()
def test_core_is_host_neutral():
 forbidden=('wp_enqueue_','wp_localize_','wp_rest','wp-json','wp-content','wp-admin','wordpress/sustainable-catalyst-workspace','window.scworkspaceidentity','sc_workspace_')
 for path in CORE:
  text=path.read_text().lower()
  for marker in forbidden: assert marker not in text,f'{path} contains host coupling marker: {marker}'
def test_host_contract_no_longer_owns_transport_or_identity():
 text=CORE[0].read_text();required=text.split('const REQUIRED_METHODS',1)[1].split(']);',1)[0];assert "'request'" not in required;assert "'identity'" not in required;assert "'configuration'" in required;assert "'resolveAsset'" in required
def test_wordpress_transport_has_no_authentication():
 text=WP_TRANSPORT.read_text();assert 'X-WP-Nonce' not in text;assert 'restNonce' not in text;assert 'authenticationEmbedded:false' in text
def test_wordpress_auth_is_separate():
 text=WP_AUTH.read_text();assert 'X-WP-Nonce' in text;assert 'SCWorkspaceIdentity' in text;assert 'fetch(' not in text;assert '.request(' not in text
def test_shell_loads_decoupled_layers():
 text=SHELL.read_text()
 for marker in ('transportRuntimeUrl','authContextRuntimeUrl','apiClientRuntimeUrl','transportAdapterUrl','authAdapterUrl','SCWorkspaceTransportFactory','SCWorkspaceAuthContextFactory','SCWorkspaceApiClientFactory'): assert marker in text
def test_kernel_registers_decoupled_services():
 text=CORE[1].read_text()
 for marker in ('registerTransport','registerAuth','registerApiClient','transportRegistered','authRegistered','apiClientRegistered'):assert marker in text
def test_lifecycle_continuity():
 text=LIFECYCLE.read_text();assert "const INTERACTION_RUNTIME_VERSION = '3.46.2.0';" in text;assert 'function deleteActiveProjectFromDevice()' in text;assert 'compatibility-project-lifecycle' in text
def test_deployment_guard():
 text=DEPLOYMENT.read_text()
 for marker in ('transport_runtime','auth_context_runtime','api_client_runtime','wordpress_transport_adapter','wordpress_auth_adapter','transport_auth_api_boundary_ok'):assert marker in text
 assert "const PREVIOUS_RELEASE = '3.46.1.0';" in text;assert "const ROLLBACK_RELEASE = '3.46.1.0';" in text
def test_main_shell_zero_wp_dependencies():
 text=WORKSPACE.read_text();m=re.search(r"wp_enqueue_script\(\s*'sc-workspace-v241',\s*SC_WORKSPACE_URL \. 'assets/js/workspace-v3\.46\.2\.0\.js',\s*(array\([\s\S]*?\)),\s*SC_WORKSPACE_VERSION,\s*true\s*\)",text);assert m;assert re.sub(r'\s+','',m.group(1))=='array()'
