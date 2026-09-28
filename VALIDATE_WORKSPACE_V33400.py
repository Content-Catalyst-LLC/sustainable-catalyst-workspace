#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve(); backend=root/'backend' if (root/'backend/neural-runtime/service.py').exists() else root; repo=root if backend!=root else None
def req(c,m):
    if not c: raise SystemExit('ERROR: '+m)
def txt(r): return (backend/r).read_text()
config=txt('app/config.py'); main=txt('app/main.py'); poly=txt('app/polyglot.py'); neural=txt('neural-runtime/service.py')
req('service_version: str = "3.34.0"' in config,'backend version is not 3.34.0'); req('SERVICE_VERSION = "3.34.0"' in neural,'neural version is not 3.34.0')
ops=['workspace.neural.gnn-split-plan','workspace.neural.gnn-training-plan','workspace.neural.gnn-train','workspace.neural.gnn-checkpoint-create','workspace.neural.gnn-checkpoint-resume']
for op in ops:req(op in neural and op in poly,f'v3.34 operation missing: {op}')
for op in ['workspace.neural.graph-tensor-contract','workspace.neural.gnn-forward','workspace.neural.gnn-infer','workspace.neural.certification-report']:
    req(op in neural and op in poly,f'prior neural operation not preserved: {op}')
for s in ['GNN_SPLIT_PLAN_SCHEMA','GNN_TRAINING_PLAN_SCHEMA','GNN_TRAINING_ARTIFACT_SCHEMA','GNN_CHECKPOINT_ARTIFACT_SCHEMA','GNN_TRAINING_TASKS','_gnn_train','_gnn_checkpoint_resume']:
    req(s in neural,f'v3.34 implementation missing: {s}')
req('"neuralRuntimeBoundedOperations": 62' in main,'operation count is not 62'); req('"neuralGnnTrainingEnabled": True' in main,'GNN training is not enabled')
req('"gnnTrainingEnabled": True' in neural,'neural health does not enable GNN training'); req('opaqueSerializedOptimizerStateAllowed' in neural,'checkpoint serialization boundary missing')
req('torch.save(' not in neural and 'torch.load(' not in neural,'opaque torch serialization unexpectedly enabled')
for media in ['application/vnd.sc.workspace.neural-gnn-training+json','application/vnd.sc.workspace.neural-gnn-checkpoint+json']:
    req(media in poly,f'governed artifact persistence missing: {media}')
if repo is not None:
    p=repo/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
    if p.exists(): req('3.34.0' in p.read_text(),'WordPress version not advanced')
print('PASS: Workspace v3.34.0 Graph Neural Network Training Runtime validation')
