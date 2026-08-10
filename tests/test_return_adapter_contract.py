import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.44.0.js'
HELPER=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-return-adapter-v1.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'
class ReturnAdapterTests(unittest.TestCase):
    def test_workspace_adapter_runtime(self):
        t=JS.read_text()
        for token in (
            "const RETURN_ADAPTER_SCHEMA = 'sc-workspace-return-adapter/1.0'",
            'const RETURN_ADAPTERS = {',
            'function normalizeDestinationKey',
            'function adaptReturnPacket',
            'automatic && !entry',
            'entry.destination !== packet.destination',
            'window.SCWorkspaceReturnAdapter',
            "window.addEventListener('message'",
            'event.origin !== window.location.origin',
        ):
            self.assertIn(token,t)
    def test_producer_helper(self):
        t=HELPER.read_text()
        for token in (
            "const ADAPTER_SCHEMA='sc-workspace-return-adapter/1.0'",
            "const OUTBOUND_KEY='sc_workspace_handoff_v2'",
            "const RETURN_KEY='sc_workspace_handoff_return_v1'",
            'window.SCWorkspaceToolReturnAdapter',
            'postMessage',
            'window.location.assign',
        ):
            self.assertIn(token,t)
    def test_php_contract(self):
        t=PHP.read_text()
        for token in (
            "'/adapter-contract'",
            "'schema' => 'sc-workspace-return-adapter-contract/1.0'",
            "'adapter_schema' => 'sc-workspace-return-adapter/1.0'",
            "'automatic_return_requires_local_handoff' => true",
            "'same_origin_postmessage_return' => true",
            'data-scw-return-adapters',
        ):
            self.assertIn(token,t)
    def test_manifest_preserves_adapter_during_traceability_migration(self):
        m=json.loads((ROOT/'release-manifest-v0.44.0.json').read_text())
        self.assertEqual(m['storage_schema_version'],35)
        self.assertEqual(m['project_schema'],'sc-workspace-project/20.0')
        self.assertEqual(m['handoff_adapter_schema'],'sc-workspace-return-adapter/1.0')
        self.assertEqual(m['cloud_sync'],'explicit-project-enrollment')
        self.assertEqual(m['server_project_storage'],'manual-backup-plus-explicit-sync-head')
if __name__=='__main__': unittest.main()
