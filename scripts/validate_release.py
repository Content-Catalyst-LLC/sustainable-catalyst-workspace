from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/validate_wordpress_deployment_hardening.py')],check=True,cwd=R)
print('PASS - v0.81.0 release validator')
