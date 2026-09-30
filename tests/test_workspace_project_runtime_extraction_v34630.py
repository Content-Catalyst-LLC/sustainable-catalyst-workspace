from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "wordpress/sustainable-catalyst-workspace"
PLUGIN = P / "sustainable-catalyst-workspace.php"
WORKSPACE = P / "includes/class-sc-workspace.php"
DEPLOYMENT = P / "includes/class-sc-workspace-deployment.php"
CONFIG = ROOT / "backend/app/config.py"
PROJECT = ROOT / "app/projects/workspace-project-runtime-v34630.js"
KERNEL = ROOT / "app/core/workspace-application-kernel-v34630.js"
SHELL = P / "assets/js/workspace-v3.46.3.0.js"
COMPAT = P / "assets/js/sc-workspace-local-project-compat-v34630.js"
WP_PROJECT = P / "assets/js/sc-workspace-project-runtime-v34630.js"

def test_release_identity():
    assert "Version: 3.46.3.0" in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.3.0');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.3.0"' in CONFIG.read_text()

def test_project_runtime_is_canonical_and_host_neutral():
    assert PROJECT.is_file()
    text = PROJECT.read_text()
    assert "sc-workspace-project-runtime/1.0" in text
    assert "sc-workspace-project-state-port/1.0" in text
    forbidden = (
        "wp_enqueue_", "wp_localize_", "wp_rest", "wp-json", "wp-content",
        "wp-admin", "wordpress/sustainable-catalyst-workspace",
        "window.scworkspaceidentity", "sc_workspace_",
    )
    lower = text.lower()
    for marker in forbidden:
        assert marker not in lower
    assert WP_PROJECT.read_text() == PROJECT.read_text()

def test_project_runtime_owns_lifecycle_orchestration():
    text = PROJECT.read_text()
    assert "function createProject(input)" in text
    assert "function openProject(projectId, options)" in text
    assert "function deleteProject(projectId, options)" in text
    assert "port.replaceProjects" in text
    assert "port.setActiveProjectId" in text
    assert "project-delete-reference-cleanup" in text
    assert "so the project was restored in memory" in text

def test_compatibility_bundle_is_state_ui_port_not_lifecycle_provider():
    text = COMPAT.read_text()
    assert "SCWorkspaceProjectRuntimeFactory" in text
    assert "sc-workspace-compatibility-project-state-port/1.0" in text
    assert "compatibility-project-lifecycle" not in text
    assert "applicationKernel.registerProjectLifecycle(projectRuntime)" in text

def test_primary_create_routes_through_kernel():
    text = COMPAT.read_text()
    assert "applicationKernel.createProject({" in text
    submit = text.split("if (createForm) createForm.addEventListener('submit'",1)[1].split("root.querySelectorAll('[data-scw-filter]')",1)[0]
    assert "projectTemplate(" not in submit
    assert "state.projects.push(" not in submit

def test_primary_open_routes_through_kernel():
    text = COMPAT.read_text()
    card = text.split("function projectCard(project)",1)[1].split("function renderList()",1)[0]
    assert "applicationKernel.openProject(project.id" in card
    assert "state.activeProjectId = project.id" not in card

def test_delete_delegate_contains_no_local_removal_logic():
    text = COMPAT.read_text()
    block = text.split("function deleteActiveProjectFromDevice()",1)[1].split("bindControl('[data-scw-delete]'",1)[0]
    assert "applicationKernel.deleteProject(project.id" in block
    assert "state.projects = state.projects.filter" not in block
    assert "cleanKnowledgeProjectReferences" not in block

def test_shell_loads_project_runtime_before_compatibility():
    text = SHELL.read_text()
    assert "projectRuntimeUrl" in text
    assert "SCWorkspaceProjectRuntimeFactory" in text
    assert "project-runtime" in text
    assert text.index("loadScriptAsset(projectRuntimeUrl") < text.index("loadCompat('v3.46.3.0-core-interaction-continuity')")

def test_kernel_reports_extracted_runtime():
    text = KERNEL.read_text()
    assert "projectRuntimeExtracted" in text
    assert "sc-workspace-project-runtime/1.0" in text
    assert "projectRuntime()" in text

def test_deployment_guard_requires_project_runtime():
    text = DEPLOYMENT.read_text()
    assert "'project_runtime' => 'assets/js/sc-workspace-project-runtime-v34630.js'" in text
    assert "const MIN_PROJECT_RUNTIME_BYTES" in text
    assert "$project_runtime_ok" in text
    assert "const PREVIOUS_RELEASE = '3.46.2.0';" in text
    assert "const ROLLBACK_RELEASE = '3.46.2.0';" in text

def test_main_shell_has_zero_wordpress_script_dependencies():
    text = WORKSPACE.read_text()
    m = re.search(
        r"wp_enqueue_script\(\s*'sc-workspace-v241',\s*"
        r"SC_WORKSPACE_URL \. 'assets/js/workspace-v3\.46\.3\.0\.js',\s*"
        r"(array\([\s\S]*?\)),\s*SC_WORKSPACE_VERSION,\s*true\s*\)",
        text,
    )
    assert m
    assert re.sub(r"\s+", "", m.group(1)) == "array()"
