from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/validate_universal_workspace_search.py')],check=True,cwd=R)
print('PASS - v1.2.0 release validator')
