from pathlib import Path
import json, py_compile
root=Path(__file__).resolve().parents[1]
assert (root/'backend/uncertainty-runtime/service.py').exists()
assert (root/'backend/migrations/020_monte_carlo_uncertainty_quantification.sql').exists()
manifest=json.loads((root/'release-manifest-v2.20.0.json').read_text())
assert manifest['version']=='2.20.0' and manifest['operations']==8
for p in [root/'backend/app/config.py',root/'backend/app/models.py',root/'backend/app/polyglot.py',root/'backend/app/main.py',root/'backend/app/routing.py',root/'backend/uncertainty-runtime/service.py']:
    py_compile.compile(str(p),doraise=True)
print('PASS: Workspace v2.20.0 Monte Carlo/UQ source contract')
