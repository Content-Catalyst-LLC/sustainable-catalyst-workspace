from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/validate_live_production_certification_release_signoff.py')],check=True,cwd=R)
print('PASS - v0.83.0 release validator')
