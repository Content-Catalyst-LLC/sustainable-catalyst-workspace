from pathlib import Path
import subprocess,sys
from release_lineage import current_release, load_manifest, load_registry
R=Path(__file__).resolve().parents[1]; CUR=current_release(R)
MAN=load_manifest(R,'0.84.0'); OLD=load_manifest(R,'0.83.0'); REG=load_registry(R,'0.84.0')
def check(x,l):
    if not x: raise SystemExit('FAIL - historical v0.84.0 Production Sign-Off Closure & 1.0 Release Readiness gate: '+l)
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.84.0','0.83.0','Production Sign-Off Closure & 1.0 Release Readiness'),'historical release lineage')
check((REG['public_version'],REG['previous_version'])==('0.84.0','0.83.0'),'historical registry lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0','historical schema freeze')
check(MAN['production_ga_readiness']['production_signoff_release']=='0.83.0','historical signoff prerequisite')
for f in ['schemas/sc-workspace-ga-readiness-v1.schema.json','schemas/sc-workspace-ga-readiness-dossier-v1.schema.json','docs/PRODUCTION_SIGNOFF_CLOSURE_1_0_RELEASE_READINESS_V0840.md','RELEASE_NOTES_0.84.0.md']:
    check((R/f).exists(),f)
subprocess.run([sys.executable,str(R/'scripts/validate_live_production_certification_release_signoff.py')],check=True,cwd=R)
print('PASS - historical v0.84.0 Production Sign-Off Closure & 1.0 Release Readiness source gate under current v'+CUR.version)
