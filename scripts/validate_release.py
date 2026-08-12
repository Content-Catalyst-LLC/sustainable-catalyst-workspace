from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/validate_public_beta_iii_defect_closure.py')],check=True,cwd=R)
print('PASS - v0.79.0 release validator')
