from __future__ import annotations
import importlib.util, pathlib, math
from fastapi import HTTPException

def load_service():
    p=pathlib.Path(__file__).parents[1]/'neural-runtime/service.py'; spec=importlib.util.spec_from_file_location('scw_v335_service',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def model(m,out=2,adapter='gcn'):
    rows=2 if adapter=='gcn' else 4
    return {'schema':m.GNN_MODEL_SPEC_SCHEMA,'adapter':adapter,'inputFeatures':2,'outputFeatures':out,'activation':'identity','weights':[[0.6 if i==j%rows else 0.15 for j in range(out)] for i in range(rows)],'bias':[0.0]*out,'addSelfLoops':True}

def graph(): return {'nodeFeatures':[[1.,0.],[0.,1.],[1.,1.],[0.2,0.8]],'nodeIds':['a','b','c','d'],'edges':[[0,1],[1,2],[2,3]],'directed':False}

def test_node_multiclass_evaluation():
    m=load_service(); p=graph(); p.update({'task':'node-multiclass-classification','labels':[0,1,0,1],'modelSpec':model(m,2),'evaluationIndices':[0,1,2,3]}); r=m._gnn_evaluate(p); assert r['gnnEvaluationArtifact']['schema']==m.GNN_EVALUATION_ARTIFACT_SCHEMA; assert 0<=r['metrics']['accuracy']<=1

def test_binary_calibration():
    m=load_service(); p=graph(); p.update({'task':'node-binary-classification','labels':[0,1,1,0],'modelSpec':model(m,1),'bins':4}); r=m._gnn_calibration_report(p); assert len(r['bins'])<=4; assert r['expectedCalibrationError']>=0

def test_gradient_and_occlusion_explainability():
    m=load_service(); p=graph(); p.update({'modelSpec':model(m,2),'targetNodeIndex':2,'targetOutputIndex':1}); a=m._gnn_explain_gradient(p); b=m._gnn_explain_occlusion(p); assert len(a['attributions'])==4 and len(a['attributions'][0])==2; assert len(b['featureScores'])==2; assert a['gnnExplainabilityArtifact']['isObservedEvidence'] is False

def test_embeddings_similarity_neighbors():
    m=load_service(); p=graph(); p.update({'modelSpec':model(m,2),'normalization':'l2'}); e=m._gnn_embedding_extract(p); assert len(e['nodeEmbeddings'])==4 and len(e['graphEmbedding'])==2
    s=dict(p); s.update({'metric':'cosine','pairs':[[0,1],[0,2]]}); rr=m._gnn_embedding_similarity(s); assert len(rr['results'])==2
    n=dict(p); n.update({'metric':'cosine','queryNodeIndices':[0],'topK':2}); nn=m._gnn_embedding_neighbors(n); assert len(nn['results'][0]['neighbors'])==2

def test_boundaries():
    m=load_service(); p=graph(); p.update({'modelSpec':model(m,2),'metric':'manhattan','pairs':[[0,1]]})
    try: m._gnn_embedding_similarity(p); assert False
    except HTTPException as e: assert e.status_code==400
