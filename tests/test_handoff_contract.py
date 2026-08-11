import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.61.0.js'
PHP=ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'

class HandoffContractTests(unittest.TestCase):
    def test_schemas(self):
        ledger=json.loads((ROOT/'schemas/sc-workspace-handoff-ledger-v1.schema.json').read_text())
        ret=json.loads((ROOT/'schemas/sc-workspace-handoff-return-v1.schema.json').read_text())
        project=json.loads((ROOT/'schemas/sc-workspace-project-v8.schema.json').read_text())
        self.assertEqual(ledger['properties']['schema']['const'],'sc-workspace-handoff-ledger/1.0')
        self.assertEqual(ledger['properties']['entries']['maxItems'],150)
        self.assertEqual(ret['properties']['schema']['const'],'sc-workspace-handoff-return/1.0')
        self.assertEqual(ret['properties']['artifacts']['maxItems'],20)
        self.assertEqual(project['properties']['schema']['const'],'sc-workspace-project/8.0')
        self.assertEqual(project['properties']['handoffs']['$ref'],'sc-workspace-handoff-ledger-v1.schema.json')
    def test_js_handoff_runtime(self):
        t=JS.read_text()
        for token in ("const HANDOFF_SCHEMA = 'sc-workspace-handoff/2.0'","const HANDOFF_LEDGER_SCHEMA = 'sc-workspace-handoff-ledger/1.0'","const HANDOFF_RETURN_SCHEMA = 'sc-workspace-handoff-return/1.0'",'function createHandoff','function ingestReturnPacket','function renderHandoffs','function downloadReturnTemplate',"target.searchParams.set('sc_workspace_handoff', handoff.id)","target.searchParams.set('sc_workspace_intent', handoff.intent)",'returnStorageKey: HANDOFF_RETURN_KEY',"obj.provenance.sourceType = 'tool'"):
            self.assertIn(token,t)
    def test_privacy_boundary(self):
        t=JS.read_text()
        click=t[t.index("root.querySelectorAll('[data-scw-tool]')"):]
        for forbidden in ("searchParams.set('title'","searchParams.set('content'","searchParams.set('notes'","searchParams.set('summary'","searchParams.set('tags'"):
            self.assertNotIn(forbidden,click)
    def test_php_contract(self):
        t=PHP.read_text()
        for token in ("'/handoff-contract'","'schema' => 'sc-workspace-handoff-contract/2.1'","'ledger_schema' => 'sc-workspace-handoff-ledger/1.0'","'return_schema' => 'sc-workspace-handoff-return/1.0'","'content_in_query_string' => false","'server_broker' => false",'CROSS-PRODUCT HANDOFFS','data-scw-handoff-list'):
            self.assertIn(token,t)
if __name__=='__main__': unittest.main()
