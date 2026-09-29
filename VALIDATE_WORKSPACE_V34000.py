#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
def req(rel,needle):
 p=root/rel
 if not p.exists(): raise SystemExit(f'ERROR: missing {rel}')
 t=p.read_text(errors='replace')
 if needle not in t: raise SystemExit(f'ERROR: {needle!r} missing from {rel}')
req('backend/app/config.py','service_version: str = "3.40.0"')
req('backend/neural-runtime/service.py','SERVICE_VERSION = "3.40.0"')
for op in ['research-package-plan','research-package-create','research-package-verify','research-package-inspect','research-package-reproduction-plan','research-package-reproduction-verify','research-package-export','research-package-lineage']:
 req('backend/neural-runtime/service.py','workspace.neural.'+op)
 req('backend/app/polyglot.py','workspace.neural.'+op)
req('backend/app/main.py','"neuralRuntimeBoundedOperations": 109')
req('backend/app/main.py','reproducibleDeepLearningResearchPackagesRuntime')
req('wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php','Version: 3.40.0')
req('wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php','workspace-v3.40.0.css')
assert (root/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v3.40.0.css').exists()
assert (root/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v3.40.0.js').exists()
print('PASS: Workspace v3.40.0 Reproducible Deep Learning Research Packages validation')
