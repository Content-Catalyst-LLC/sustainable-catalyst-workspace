from pathlib import Path
root=Path(__file__).resolve().parents[1]
assert (root/'backend/app/notebook_orchestration.py').exists()
assert (root/'backend/migrations/026_server_side_notebook_artifact_orchestration.sql').exists()
assert 'service_version: str = "2.26.0"' in (root/'backend/app/config.py').read_text()
wp=(root/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text()
assert 'Version: 2.26.0' in wp
js=root/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.26.0.js'
css=root/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.26.0.css'
assert js.stat().st_size > 500000 and css.stat().st_size > 250000
assert 'browserSchedulesDependencies:false' in js.read_text()
print('PASS: Workspace v2.26.0 server-side notebook/artifact orchestration contract')
