from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/validate_production_signoff_closure_ga_readiness.py')],check=True,cwd=R)
print('PASS - v0.84.0 release validator')
