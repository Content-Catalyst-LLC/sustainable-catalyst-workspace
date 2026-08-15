from pathlib import Path
import json, subprocess, sys
from release_lineage import current_release, load_manifest, validate_current_release_lineage
R=Path(__file__).resolve().parents[1]
CUR=current_release(R)
def check(x,l):
    if not x: raise SystemExit('FAIL - v0.82.1 Installer & Validation Lineage Repair gate: '+l)
lineage=validate_current_release_lineage(R,'0.82.1','0.82.0')
check(lineage['ok'],'current release lineage: '+('; '.join(lineage['errors']) if lineage['errors'] else 'unknown'))
MAN=load_manifest(R,'0.82.1'); OLD=load_manifest(R,'0.82.0')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.82.1','0.82.0','Production Certification Installer & Validation Lineage Repair'),'release lineage')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:
    check(MAN[k]==OLD[k],'frozen '+k)
check(MAN['object_types']==OLD['object_types'],'frozen object types')
check(MAN['rest_routes']==OLD['rest_routes'],'no REST changes')
check(MAN['schema_migration_required'] is False,'no schema migration')
repair=MAN['production_certification_installer_validation_lineage_repair']
for k in ['release_candidate','feature_freeze','historical_contract_identity_preserved','current_release_discovery','source_archive_lineage_preflight','post_rsync_lineage_gate','pre_commit_lineage_gate','post_stage_lineage_gate','wordPress_header_lineage_check','runtime_constant_lineage_check','manifest_lineage_check','registry_lineage_check','cumulative_asset_lineage_check','deployment_predecessor_lineage_check','production_certification_predecessor_lineage_check','stale_archive_rejected','stale_target_rejected','no_commit_on_lineage_failure','no_push_on_lineage_failure','rollback_schema_compatible']:
    check(repair.get(k) is True,k)
for k in ['new_product_subsystem','schema_migration_required','automatic_rollback','automatic_cache_purge','automatic_project_migration','project_data_inspected','project_data_mutated','telemetry']:
    check(repair.get(k) is False,k)
check(repair['rollback_release']=='0.81.0','rollback release')
check((R/'history/release-manifest-v0.82.0.json').exists(),'v0.82 manifest history')
check((R/'history/workspace-product-record-v0.82.0.json').exists(),'v0.82 registry history')
for f in ['scripts/release_lineage.py','scripts/verify_release_lineage.py','docs/PRODUCTION_CERTIFICATION_INSTALLER_VALIDATION_LINEAGE_REPAIR_V0821.md','RELEASE_NOTES_0.82.1.md','scripts/verify_wordpress_production_v0_82_1.sh']:
    check((R/f).exists(),f)
security=(R/'scripts/validate_security_privacy_audit_ii.py').read_text()
check('current_release(R)' in security and 'CUR.script_path' in security,'security gate derives current runtime')
check('workspace-v0.82.0.js' not in security and "Version: 0.82.0" not in security,'security gate has no frozen current-version literal')
deployment=(R/'scripts/validate_wordpress_deployment_hardening.py').read_text()
production=(R/'scripts/validate_production_smoke_cache_rollback_certification.py').read_text()
check('current_release(R)' in deployment and 'current_release(R)' in production,'inherited deployment/certification gates derive current release')
# Run inherited gates exactly once from the top-level repair validator.
for script in [
    'validate_public_beta_iii_defect_closure.py',
    'validate_security_privacy_audit_ii.py',
    'validate_accessibility_performance_final_audit.py',
    'validate_workspace_release_candidate_i.py',
    'validate_wordpress_deployment_hardening.py',
    'validate_production_smoke_cache_rollback_certification.py',
]:
    subprocess.run([sys.executable,str(R/'scripts'/script)],check=True,cwd=R)
print('PASS - v0.82.1 Production Certification Installer & Validation Lineage Repair source gate')
