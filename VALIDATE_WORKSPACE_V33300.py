#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
backend = root/'backend' if (root/'backend/neural-runtime/service.py').exists() else root
repo = root if backend != root else None

def req(cond, msg):
    if not cond: raise SystemExit('ERROR: ' + msg)

def txt(rel): return (backend/rel).read_text()

config = txt('app/config.py')
main = txt('app/main.py')
poly = txt('app/polyglot.py')
neural = txt('neural-runtime/service.py')
req('service_version: str = "3.33.0"' in config, 'backend version is not 3.33.0')
req('SERVICE_VERSION = "3.33.0"' in neural, 'neural runtime version is not 3.33.0')
ops = [
    'workspace.neural.graph-tensor-contract','workspace.neural.graph-dataset-project','workspace.neural.gnn-model-summary',
    'workspace.neural.gnn-forward','workspace.neural.gnn-infer'
]
for op in ops:
    req(op in neural and op in poly, f'GNN operation missing from runtime/registry: {op}')
for op in ['workspace.neural.certification-plan','workspace.neural.certification-execute','workspace.neural.certification-verify','workspace.neural.certification-report']:
    req(op in neural and op in poly, f'v3.32 certification operation was not preserved: {op}')
for sym in [
    'GRAPH_TENSOR_CONTRACT_SCHEMA = "sc-workspace-neural-graph-tensor-contract/1.0"',
    'GRAPH_DATASET_PROJECTION_SCHEMA = "sc-workspace-neural-graph-dataset-projection/1.0"',
    'GNN_MODEL_SPEC_SCHEMA = "sc-workspace-neural-gnn-model-spec/1.0"',
    'GNN_EXECUTION_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-execution-artifact/1.0"',
    'GNN_PREDICTION_ARTIFACT_SCHEMA = "sc-workspace-neural-gnn-prediction-artifact/1.0"',
    'GNN_ADAPTERS = {"gcn", "graphsage-mean"}',
    'MAX_GRAPH_NODES', 'MAX_GRAPH_EDGES', '_graph_dataset_project', '_gnn_forward', '_gnn_infer'
]: req(sym in neural, f'v3.33 implementation missing: {sym}')
req('"neuralRuntimeBoundedOperations": 57' in main, 'Workspace neural operation count is not 57')
req('"graphNeuralNetworkRuntimeFoundation": True' in main, 'Workspace GNN capability missing')
req('"neuralGnnTrainingEnabled": False' in main, 'GNN training must remain disabled in v3.33.0')
for media in ['application/vnd.sc.workspace.neural-graph-projection+json','application/vnd.sc.workspace.neural-gnn-execution+json','application/vnd.sc.workspace.neural-gnn-prediction+json']:
    req(media in poly, f'GNN artifact persistence missing: {media}')
req('workspaceGnnArtifactId' in poly and 'graphNeuralNetworkRuntimeFoundation' in poly, 'GNN receipt lineage missing')
req('"inferredEdges": False' in neural and '"inferredFeatures": False' in neural, 'graph projection inference boundary missing')
req('"isObservedEvidence": False' in neural and 'model-derived-node-output-not-source-evidence' in neural, 'prediction/evidence boundary missing')
req('GNN modelSpec does not accept code, packages, runtime URLs, credentials, or serialized modules' in neural, 'nested GNN model security gate missing')
req('gnnTrainingEnabled": False' in neural, 'neural health does not declare GNN training disabled')
req('torch.save(' not in neural and 'torch.load(' not in neural, 'raw torch serialization unexpectedly enabled')
if repo is not None:
    plugin = repo/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
    if plugin.exists(): req('3.33.0' in plugin.read_text(), 'WordPress version was not advanced to 3.33.0')
print('PASS: Workspace v3.33.0 Graph Neural Network Runtime Foundation validation')
