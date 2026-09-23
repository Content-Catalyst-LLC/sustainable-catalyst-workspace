#!/usr/bin/env python3
# Generated-contract source for Workspace v3.12.0.
from pathlib import Path
import ast,json
root=Path(__file__).resolve().parents[1]
tree=ast.parse((root/'backend/app/client_contracts.py').read_text()); eps=None
for n in tree.body:
    if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name) and n.target.id=='TYPED_ENDPOINTS': eps=ast.literal_eval(n.value)
assert eps is not None
ts="export const SCW_TYPED_CONTRACT_VERSION = '3.12.0';\nexport const SCW_TYPED_ENDPOINTS = "+json.dumps(eps,indent=2)+" as const;\nexport type SCWTypedEndpointKey = keyof typeof SCW_TYPED_ENDPOINTS;\n"
(root/'frontend/typed-client/src/00-generated-contracts.ts').write_text(ts)
(root/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-typed-client-v31200.js').write_text("window.SCW_TYPED_CONTRACT_VERSION='3.12.0';\nwindow.SCW_TYPED_ENDPOINTS="+json.dumps(eps,separators=(',',':'))+";\n")
print('PASS: Workspace v3.12.0 typed client generated endpoints=%d'%len(eps))
