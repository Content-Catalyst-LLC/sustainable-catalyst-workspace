from pathlib import Path
import subprocess,sys
from release_lineage import current_release,load_manifest,load_registry
R=Path(__file__).resolve().parents[1];CUR=current_release(R);P=R/'wordpress/sustainable-catalyst-workspace'
MAN=load_manifest(R,'1.0.0');OLD=load_manifest(R,'0.84.0');REG=load_registry(R,'1.0.0');GA=(P/'includes/class-sc-workspace-general-availability.php').read_text();RUN=(P/'assets/js/sc-workspace-general-availability-v1.js').read_text()
def check(x,l):
    if not x: raise SystemExit('FAIL - historical v1.0.0 General Availability gate: '+l)
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('1.0.0','0.84.0','General Availability'),'historical release lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'],REG['lifecycle_state'],REG['release_channel'])==('1.0.0','0.84.0','General Availability','production','stable'),'historical registry identity')
for k in ['storage_schema_version','project_schema','export_schema','object_schema','research_schema']:check(MAN[k]==OLD[k],'historical frozen '+k)
check(MAN['object_types']==OLD['object_types'],'historical frozen object types');check(MAN['schema_migration_required'] is False,'historical no schema migration')
check(set(MAN['rest_routes'])-set(OLD['rest_routes'])=={'/wp-json/sc-workspace/v1/general-availability-contract'},'historical GA REST route')
g=MAN['general_availability'];check(g['readiness_release']=='0.84.0' and g['rollback_release']=='0.84.0','historical readiness/rollback')
check("READINESS_RELEASE = '0.84.0'" in GA and "const RELEASE_VERSION='1.0.0'" in RUN,'historical GA runtime retained')
for f in ['schemas/sc-workspace-general-availability-v1.schema.json','schemas/sc-workspace-general-availability-certificate-v1.schema.json','docs/GENERAL_AVAILABILITY_V100.md','RELEASE_NOTES_1.0.0.md']:check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_production_signoff_closure_ga_readiness.py')],check=True,cwd=R)
print('PASS - historical v1.0.0 General Availability source gate under current v'+CUR.version)
