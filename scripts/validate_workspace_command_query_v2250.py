from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
assert 'service_version: str = "2.25.0"' in (root/'backend/app/config.py').read_text()
main=(root/'backend/app/main.py').read_text(); cq=(root/'backend/app/command_query.py').read_text()
for x in ['/v1/command-query','/v1/commands/execute','/v1/queries/execute','/v1/read-models/workspace-overview']:
    assert x in main,x
assert 'queriesMutate": False' in cq
assert 'browserCommandAuthority": False' in cq
assert (root/'backend/migrations/025_workspace_command_query_api.sql').exists()
wp=root/'wordpress/sustainable-catalyst-workspace'
assert (wp/'assets/js/workspace-v2.25.0.js').stat().st_size > 800000
assert (wp/'assets/css/workspace-v2.25.0.css').stat().st_size > 300000
assert 'workspace-v2.25.0.js' in (wp/'includes/class-sc-workspace.php').read_text()
json.load(open(root/'release-manifest-v2.25.0.json'))
print('PASS - Workspace v2.25.0 command/query API contract')
