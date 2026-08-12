from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.73.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.73.0.json').read_text())
MAINP=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'; RAW=MAINP.read_bytes(); MAIN=MAINP.read_text(); HEAD=RAW[:8192].decode('utf-8',errors='replace')
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-shared-review-handoff-v1.js').read_text(); UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-shared-review-handoff-ui-v1.js').read_text(); CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.73.0.css').read_text()
def check(ok,label):
 if not ok: raise SystemExit('FAIL - '+label)
check('Version: 0.73.0' in MAIN and "SC_WORKSPACE_VERSION', '0.73.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.73.0','0.72.0','Collaboration & Shared Review Hardening'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'canonical schemas stable')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.73.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
 m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M); check(bool(m) and m.group(1).strip()==expected,'8KB header '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512 and RAW.find(b'Description:')<1024,'compact plugin header')
check("'sc-workspace-v0730'" in PHP and 'workspace-v0.73.0.js' in PHP and 'workspace-v0.73.0.css' in PHP,'current cumulative assets')
check("wp_localize_script('sc-workspace-v0730'" in PHP,'current localization handle')
check("'/collaboration-review-hardening-contract'" in PHP and 'collaboration_review_hardening_contract' in PHP,'collaboration hardening REST')
check('/wp-json/sc-workspace/v1/collaboration-review-hardening-contract' in MAN['rest_routes'],'manifest REST route')
h=MAN['collaboration_review_hardening']
for k in ['source_revision_fingerprint','stale_response_detection','duplicate_response_commit_blocked','stale_response_requires_owner_acknowledgement','reconciliation_receipt']: check(h[k] is True,'hardening '+k)
for k in ['canonical_mutation','proposal_acceptance_applies_change','live_coediting','server_collaboration','automatic_send','schema_migration_required']: check(h[k] is False,'hardening boundary '+k)
for marker in ['sourceSnapshotFingerprint','assessResponseImport','commitResponseHardened','RECEIPT_STORAGE_KEY','duplicateResponseCommitBlocked:true','staleResponseRequiresOwnerAcknowledgement:true','ownerIdentityCryptographicallyVerified:false']:
 check(marker in HELP,'helper '+marker)
check('data-scw-handoff-integrity' in PHP and 'data-scw-handoff-owner-ack' in PHP and 'Reconcile staged response' in PHP,'hardening UI markup')
check('stagedAssessment' in UI and 'ownerAcknowledged' in UI and 'reconciliation receipt recorded' in UI.lower(),'hardening UI runtime')
check('/* v0.73.0 — Collaboration & Shared Review Hardening */' in CSS,'v0.73 CSS')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0730'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0730'" in REGPHP and 'LEGACY_PENDING_KEY_V0720' in REGPHP,'registry lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.73.0','0.72.0','Collaboration & Shared Review Hardening'),'registry record')
check((ROOT/'history/release-manifest-v0.72.0.json').exists() and (ROOT/'history/workspace-product-record-v0.72.0.json').exists(),'v0.72 history retained')
for f in ['schemas/sc-workspace-collaboration-review-hardening-v1.schema.json','schemas/sc-workspace-shared-review-import-assessment-v1.schema.json','schemas/sc-workspace-shared-review-reconciliation-receipt-v1.schema.json','docs/COLLABORATION_SHARED_REVIEW_HARDENING_V0730.md','RELEASE_NOTES_0.73.0.md']:
 check((ROOT/f).exists(),f)
print('PASS - v0.73.0 release validator')
