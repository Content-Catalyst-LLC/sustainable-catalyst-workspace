from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'wordpress/sustainable-catalyst-workspace'
PLUGIN=P/'sustainable-catalyst-workspace.php'
WORKSPACE=P/'includes/class-sc-workspace.php'
DEPLOYMENT=P/'includes/class-sc-workspace-deployment.php'
COMPAT=P/'assets/js/sc-workspace-local-project-compat-v3000.js'
CONFIG=ROOT/'backend/app/config.py'
CSS=P/'assets/css/workspace-v3.46.0.3.css'
JS=P/'assets/js/workspace-v3.46.0.3.js'

def test_release():
    assert 'Version: 3.46.0.3' in PLUGIN.read_text()
    assert "define('SC_WORKSPACE_VERSION', '3.46.0.3');" in PLUGIN.read_text()
    assert 'service_version: str = "3.46.0.3"' in CONFIG.read_text()

def test_assets():
    assert CSS.stat().st_size >= 100000
    assert JS.stat().st_size >= 5000
    t=WORKSPACE.read_text()
    assert 'assets/css/workspace-v3.46.0.3.css' in t
    assert 'assets/js/workspace-v3.46.0.3.js' in t

def test_delete_is_shared_verified_action():
    t=COMPAT.read_text()
    assert 'function deleteActiveProjectFromDevice()' in t
    assert 'state.projects = state.projects.filter((item) => item.id !== projectId);' in t
    assert "persist('Project deleted from this device')" in t
    assert 'project-delete-reference-cleanup' in t
    assert 'state.projects = previousProjects;' in t

def test_delete_has_direct_and_delegated_routes():
    t=COMPAT.read_text()
    assert "bindControl('[data-scw-delete]', 'click', (event) =>" in t
    assert "target.matches('[data-scw-delete]')" in t
    assert '__scwProjectLifecycleHandled' in t

def test_decoupling_preserved():
    t=WORKSPACE.read_text()
    m=re.search(
        r"wp_enqueue_script\(\s*'sc-workspace-v241',\s*"
        r"SC_WORKSPACE_URL \. 'assets/js/workspace-v3\.46\.0\.3\.js',\s*"
        r"(array\([\s\S]*?\)),\s*SC_WORKSPACE_VERSION,\s*true\s*\)",
        t
    )
    assert m
    assert re.sub(r'\s+','',m.group(1))=='array()'

def test_release_continuity():
    t=DEPLOYMENT.read_text()
    assert "const PREVIOUS_RELEASE = '3.46.0.2';" in t
    assert "const ROLLBACK_RELEASE = '3.46.0.2';" in t
