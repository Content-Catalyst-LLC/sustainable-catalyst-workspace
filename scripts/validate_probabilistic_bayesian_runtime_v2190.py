from pathlib import Path
import json, py_compile
root=Path(__file__).resolve().parents[1]
assert (root/'backend/probability-runtime/service.py').exists()
assert (root/'backend/migrations/019_probabilistic_bayesian_runtime.sql').exists()
assert json.loads((root/'release-manifest-v2.19.0.json').read_text())['operations']==6
for p in [root/'backend/app/config.py',root/'backend/app/polyglot.py',root/'backend/app/main.py',root/'backend/app/routing.py',root/'backend/probability-runtime/service.py']:
    py_compile.compile(str(p),doraise=True)
print('PASS: Workspace v2.19.0 probabilistic/Bayesian runtime source contract')
