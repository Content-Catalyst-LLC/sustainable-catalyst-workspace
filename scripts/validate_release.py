#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.48.0.json').read_text()); REG=json.loads((ROOT/'registry/workspace-product-record-v0.48.0.json').read_text()); PREV=json.loads((ROOT/'history/release-manifest-v0.47.0.json').read_text())
MAIN=(ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php').read_text(); PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text(); JS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.48.0.js').read_text(); XPK=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-cross-project-knowledge-v1.js').read_text(); GRAPH=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-relationship-explorer-v1.js').read_text(); CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.48.0.css').read_text()
def check(v,label):
 if not v: raise SystemExit('FAIL - '+label)
 print('PASS - '+label)
check('Version: 0.48.0' in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.48.0','0.47.0','Cross-Project Knowledge'),'release lineage')
check((MAN['storage_schema_version'],MAN['project_schema'],MAN['export_schema'])==(35,'sc-workspace-project/20.0','sc-workspace-project-export/20.0'),'schema stable')
check(not MAN['schema_migration_required'] and MAN['migration']['schema_stable'] and MAN['migration']['cross_project_knowledge_only_release'] and not MAN['migration']['canonical_data_rewrite'],'cross-project-only boundary')
check(PREV['version']=='0.47.0' and PREV['knowledge_graph_schema']=='sc-workspace-knowledge-graph/2.0','v0.47.0 predecessor retained')
check(MAN['cross_project_knowledge_schema']=='sc-workspace-cross-project-knowledge/1.0' and MAN['cross_project_reference_schema']=='sc-workspace-cross-project-reference/1.0','cross-project schemas')
check('canonicalSourcePointersOnly:true' in XPK and 'copiesCanonicalContent:false' in XPK and 'sameProjectReferencesRejected:true' in XPK,'pointer-only governance')
check('unresolvedReferencesRemainVisible:true' in XPK and 'UNRESOLVED' in JS,'unresolved references visible')
check(MAN['knowledge_graph']['includes_cross_project_references'] and "source:'cross-project-knowledge-reference'" in GRAPH and 'crossProjectReferences:' in JS,'Research Graph integration')
check('CROSS-PROJECT KNOWLEDGE' in PHP and 'data-scw-cross-project-target' in PHP and 'Reference selected research' in PHP,'Cross-Project Knowledge UI')
check('exportPackage' in XPK and 'verifyPackage' in XPK and 'data-scw-cross-project-export' in PHP,'portable reference ledger')
check(not MAN['governance']['cross_project_content_copy'] and not MAN['governance']['cross_project_ownership_transfer'] and not MAN['governance']['cross_project_automatic_relationship_inference'],'no copy or inferred relation')
check('.scw-editorial-header-bar{height:4px' in CSS,'4px editorial header retained')
check((REG['public_version'],REG['previous_version'])==('0.48.0','0.47.0'),'registry lineage')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0480'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0480'" in REGPHP and 'LEGACY_PENDING_KEY_V0470' in REGPHP,'registry retry lineage')
files=list((ROOT/'schemas').glob('*.json'))+[ROOT/'release-manifest-v0.48.0.json',ROOT/'registry/workspace-product-record-v0.48.0.json']
for f in files: json.loads(f.read_text())
print(f'PASS - {len(files)} JSON schema/release records')
print('VALIDATION PASSED: Sustainable Catalyst Workspace v0.48.0 — Cross-Project Knowledge')
