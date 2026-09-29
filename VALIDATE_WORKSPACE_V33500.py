#!/usr/bin/env python3
from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve(); backend=root/'backend' if (root/'backend/neural-runtime/service.py').exists() else root; repo=root if backend!=root else None
def req(c,m):
    if not c: raise SystemExit('ERROR: '+m)
def txt(r): return (backend/r).read_text()
config=txt('app/config.py'); main=txt('app/main.py'); poly=txt('app/polyglot.py'); neural=txt('neural-runtime/service.py')
req('service_version: str = "3.35.0"' in config,'backend version is not 3.35.0'); req('SERVICE_VERSION = "3.35.0"' in neural,'neural version is not 3.35.0')
ops=['workspace.neural.gnn-evaluate','workspace.neural.gnn-calibration-report','workspace.neural.gnn-explain-gradient','workspace.neural.gnn-explain-occlusion','workspace.neural.gnn-embedding-extract','workspace.neural.gnn-embedding-similarity','workspace.neural.gnn-embedding-neighbors']
for op in ops:req(op in neural and op in poly,f'v3.35 operation missing: {op}')
for op in ['workspace.neural.gnn-train','workspace.neural.gnn-checkpoint-resume','workspace.neural.gnn-forward','workspace.neural.gnn-infer']:
    req(op in neural and op in poly,f'prior GNN operation not preserved: {op}')
for sym in ['GNN_EVALUATION_ARTIFACT_SCHEMA','GNN_CALIBRATION_ARTIFACT_SCHEMA','GNN_EXPLAINABILITY_ARTIFACT_SCHEMA','GNN_EMBEDDING_ARTIFACT_SCHEMA','_gnn_evaluate','_gnn_calibration_report','_gnn_explain_gradient','_gnn_explain_occlusion','_gnn_embedding_extract','_gnn_embedding_neighbors']:
    req(sym in neural,f'v3.35 implementation missing: {sym}')
req(main.count('"neuralRuntimeBoundedOperations": 69')>=1,'operation count is not 69'); req('"neuralGnnEvaluationExplainabilityEmbeddings": True' in main,'backend health does not expose v3.35 GNN analysis capability')
req('"gnnEvaluationExplainabilityEmbeddingsEnabled": True' in neural,'neural health does not expose v3.35 GNN analysis capability')
req('attributionPolicy' in neural and 'not-causal-evidence' in neural,'explainability interpretation guardrail missing')
req('torch.save(' not in neural and 'torch.load(' not in neural,'opaque torch serialization unexpectedly enabled')
for media in ['application/vnd.sc.workspace.neural-gnn-evaluation+json','application/vnd.sc.workspace.neural-gnn-calibration+json','application/vnd.sc.workspace.neural-gnn-explainability+json','application/vnd.sc.workspace.neural-gnn-embedding+json']:
    req(media in poly,f'governed GNN analysis artifact persistence missing: {media}')
if repo is not None:
    p=repo/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
    if p.exists(): req('3.35.0' in p.read_text(),'WordPress version not advanced')
    req((repo/'release-manifest-v3.35.0.json').exists(),'release manifest missing')
print('PASS: Workspace v3.35.0 GNN Evaluation, Explainability & Graph Embeddings validation')
