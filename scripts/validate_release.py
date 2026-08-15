from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/validate_ga_field_stabilization.py')],check=True,cwd=R)
print('PASS - v1.0.1 release validator')
