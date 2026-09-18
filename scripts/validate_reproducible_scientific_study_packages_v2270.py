from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
assert (root/'backend/app/study_packages.py').exists()
assert (root/'backend/migrations/027_reproducible_scientific_study_packages.sql').exists()
assert 'service_version: str = "2.27.0"' in (root/'backend/app/config.py').read_text()
main=(root/'backend/app/main.py').read_text(); assert '/v1/scientific-study-packages' in main and 'reproducibleScientificStudyPackages' in main
wp=(root/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); assert 'Version: 2.27.0' in wp
js=root/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v2.27.0.js'; css=root/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v2.27.0.css'
assert js.stat().st_size > 500000 and css.stat().st_size > 250000
assert 'SCWorkspaceScientificStudyPackages' in js.read_text()
manifest=json.loads((root/'release-manifest-v2.27.0.json').read_text()); assert manifest['migration']=='027_reproducible_scientific_study_packages.sql'
print('PASS: Workspace v2.27.0 reproducible scientific study package contract')
