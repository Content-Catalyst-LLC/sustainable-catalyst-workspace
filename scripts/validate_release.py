from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/validate_production_certification_installer_validation_lineage_repair.py')],check=True,cwd=R)
print('PASS - v0.82.1 release validator')
