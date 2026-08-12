from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/validate_workspace_release_candidate_i.py')],check=True,cwd=R)
print('PASS - v0.80.0 release validator')
