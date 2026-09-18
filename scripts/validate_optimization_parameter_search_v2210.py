from pathlib import Path
import json, py_compile
root=Path(__file__).resolve().parents[1]
assert (root/'backend/optimization-runtime/service.py').exists()
assert (root/'backend/migrations/021_optimization_parameter_search_runtime.sql').exists()
m=json.loads((root/'release-manifest-v2.21.0.json').read_text()); assert m['version']=='2.21.0' and m['operations']==8
for p in [root/'backend/app/config.py',root/'backend/app/models.py',root/'backend/app/polyglot.py',root/'backend/app/main.py',root/'backend/app/routing.py',root/'backend/optimization-runtime/service.py']:
    py_compile.compile(str(p),doraise=True)
for p in [root/'backend/docker-compose.example.yml',root/'backend/.env.example']:
    s=p.read_text(); assert 'optimization' in s.lower()
print('PASS: Workspace v2.21.0 Optimization & Parameter Search source contract')
