from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];P=R/'wordpress/sustainable-catalyst-workspace';m=json.loads((R/'release-manifest-v2.0.0.json').read_text());old=json.loads((R/'release-manifest-v1.15.0.json').read_text());reg=json.loads((R/'registry/workspace-product-record-v2.0.0.json').read_text());main=(P/'sustainable-catalyst-workspace.php').read_text();php=(P/'includes/class-sc-workspace.php').read_text();dep=(P/'includes/class-sc-workspace-deployment.php').read_text();prod=(P/'includes/class-sc-workspace-production-certification.php').read_text();js=(P/'assets/js/sc-workspace-connected-knowledge-v2.js').read_text()
def test_identity_and_lineage():
 assert m['version']=='2.0.0' and m['previous_version']=='1.15.0' and m['release_name']=='Connected Knowledge Workspace'
 assert reg['public_version']=='2.0.0' and reg['previous_version']=='1.15.0'
 assert 'Version: 2.0.0' in main and "SC_WORKSPACE_VERSION', '2.0.0'" in main
 assert "PREVIOUS_RELEASE = '1.15.0'" in dep and "ROLLBACK_RELEASE = '1.15.0'" in dep and "PREVIOUS_RELEASE = '1.15.0'" in prod
 assert 'workspace-v2.0.0.js' in dep and 'workspace-v2.0.0.css' in dep
def test_major_version_compatibility_boundary():
 g=m['connected_knowledge_workspace']; assert g['stable_major_release']; assert g['v1_rest_namespace_preserved']; assert g['v2_rest_namespace_available']; assert g['v1_project_compatibility']; assert g['v1_export_compatibility']; assert not g['v2_native_project_schema_introduced']; assert not g['schema_migration_required']; assert not g['automatic_migration']
 assert (m['storage_schema_version'],m['project_schema'],m['export_schema'])==(old['storage_schema_version'],old['project_schema'],old['export_schema'])
 assert '/wp-json/sc-workspace/v2/connected-knowledge-contract' in m['rest_routes']
def test_connected_contract_and_boundaries():
 g=m['connected_knowledge_workspace']; assert len(g['surfaces'])==11 and len(g['context_families'])==14; assert g['single_context_envelope']; assert g['canonical_ownership_preserved']; assert g['return_to_origin_required']; assert g['provenance_required']
 for k in ['automatic_cross_product_execution','automatic_context_upload','automatic_return_commit','automatic_ai','canonical_workspace_records_mutated','behavioral_telemetry','query_telemetry']: assert not g[k]
 for x in ['sc-workspace-connected-knowledge-workspace/2.0','v1RestNamespacePreserved:true','automaticCrossProductExecution:false','schemaMigrationRequired:false']: assert x in js
def test_wordpress_surface_and_assets():
 assert "register_rest_route('sc-workspace/v2', '/connected-knowledge-contract'" in php
 assert 'SC_Workspace_Connected_Knowledge::contract()' in php
 assert 'data-scw-connected-knowledge' in php and 'Connected Knowledge Workspace' in php
 assert 'sc-workspace-connected-knowledge-v2' in php and 'sc-workspace-connected-knowledge-ui-v2' in php
 assert 'sc-workspace-v200' in php and 'workspace-v2.0.0.js' in php and 'workspace-v2.0.0.css' in php
 assert (P/'assets/js/workspace-v2.0.0.js').exists() and (P/'assets/css/workspace-v2.0.0.css').exists()
