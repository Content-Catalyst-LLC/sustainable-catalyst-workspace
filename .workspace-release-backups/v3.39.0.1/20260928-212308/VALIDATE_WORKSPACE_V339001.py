#!/usr/bin/env python3
from pathlib import Path
import json, sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
checks=[]
def need(path, token):
    p=root/path; s=p.read_text(); assert token in s, f"missing {token} in {path}"; checks.append(str(path))
need(Path('backend/app/config.py'),'service_version: str = "3.39.0.1"')
need(Path('backend/app/polyglot.py'),'"schema":"sc-workspace-artifact-store/1.0"')
need(Path('backend/app/polyglot.py'),'existing_symbolic=get_artifact')
need(Path('backend/app/polyglot.py'),'truthValueAssigned":False')
assert 'sc-workspace-artifact-store-request/1.0' not in (root/'backend/app/polyglot.py').read_text()
need(Path('backend/tests/test_neural_symbolic_artifact_persistence_v339001.py'),'test_current_artifact_store_contract_round_trip')
need(Path('wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'),'Version: 3.39.0.1')
need(Path('wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'),'workspace-v3.39.0.1.css')
need(Path('wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php'),'workspace-v3.39.0.1.js')
manifest=json.loads((root/'release-manifest-v3.39.0.1.json').read_text())
assert manifest['version']=='3.39.0.1' and manifest['baseline']=='3.39.0' and manifest['neuralRuntimeOperations']==101
print('PASS: Workspace v3.39.0.1 Neural-Symbolic Artifact Persistence Repair validation')
print('WORKSPACE_V339001_NEURAL_RUNTIME_OPERATIONS=101')
print('WORKSPACE_V339001_DATABASE_MIGRATION=false')
