#!/usr/bin/env python3
from pathlib import Path
import ast, sys
root=Path(__file__).resolve().parent
checks={
 'backend/app/config.py':'service_version: str = "3.20.0"',
 'backend/neural-runtime/service.py':'RUNTIME = "python-pytorch-neural"',
 'backend/neural-runtime/service.py#training':'"trainingEnabled": False',
 'backend/app/polyglot.py':'RuntimeSpec("neural", "python-pytorch-neural"',
 'backend/app/routing.py':'workspace.neural.',
 'backend/docker-compose.example.yml':'sc-workspace-neural-runtime:',
 'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php':"define('SC_WORKSPACE_VERSION', '3.20.0');",
 'release-manifest-v3.20.0.json':'"typedEndpointCount": 291',
}
for key,needle in checks.items():
    rel=key.split('#',1)[0]; text=(root/rel).read_text()
    if needle not in text: raise SystemExit(f'FAIL: {key} missing {needle!r}')
ast.parse((root/'backend/app/polyglot.py').read_text())
ast.parse((root/'backend/neural-runtime/service.py').read_text())
print('PASS: Workspace v3.20.0 static release validation')
