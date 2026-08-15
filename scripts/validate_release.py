from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/validate_workspace_home_project_cockpit.py')],check=True,cwd=R)
print('PASS - v1.1.0 release validator')
