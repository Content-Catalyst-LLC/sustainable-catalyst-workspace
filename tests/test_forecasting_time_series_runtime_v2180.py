from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def test_release_identity_and_manifest():
    plugin=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
    assert 'Version: 2.18.0' in plugin and "SC_WORKSPACE_VERSION', '2.18.0'" in plugin
    manifest=json.loads((ROOT/'release-manifest-v2.18.0.json').read_text())
    assert manifest['version']=='2.18.0' and manifest['runtime']=='sc-workspace-forecast-runtime'

def test_forecast_runtime_is_bounded_and_internal():
    service=(ROOT/'backend/forecast-runtime/service.py').read_text()
    compose=(ROOT/'backend/docker-compose.example.yml').read_text()
    assert 'arbitraryCodeExecution":False' in service
    assert 'sc-workspace-forecast-runtime:' in compose
    assert 'read_only: true' in compose and 'cap_drop:' in compose and 'internal: true' in compose

def test_backend_and_wordpress_surfaces_exist():
    main=(ROOT/'backend/app/main.py').read_text()
    wp=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
    assert '/v1/polyglot/runtimes/forecast/status' in main
    assert '/v1/forecast-receipts' in main and '/v1/forecast-evaluation-receipts' in main
    assert 'backend-forecast-runtime-status' in wp and 'backend-forecast-receipts' in wp

def test_frontend_presentation_keeps_forecasting_inside_analysis_workspace():
    wp=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
    css=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.18.0.css').read_text()
    assert 'FORECASTING &amp; TIME SERIES' in wp
    assert 'scw-forecast-capability' in css
    assert 'data-scw-project-panel="analysis"' in wp

def test_literal_newline_regression_not_reintroduced():
    php='\n'.join(p.read_text(errors='ignore') for p in (ROOT/'wordpress/sustainable-catalyst-workspace').rglob('*.php'))
    assert r'</section>\n\n<section' not in php
