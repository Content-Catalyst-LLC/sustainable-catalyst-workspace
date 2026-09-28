from __future__ import annotations
import importlib.util, pathlib
from fastapi import HTTPException

def load_service():
    p=pathlib.Path(__file__).parents[1]/'neural-runtime/service.py'; spec=importlib.util.spec_from_file_location('scw_v334_service',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def model(m,out=2,adapter='gcn'):
    rows=2 if adapter=='gcn' else 4
    return {'schema':m.GNN_MODEL_SPEC_SCHEMA,'adapter':adapter,'inputFeatures':2,'outputFeatures':out,'activation':'identity','weights':[[0.01 for _ in range(out)] for _ in range(rows)],'bias':[0.0]*out,'addSelfLoops':True}

def graph(): return {'nodeFeatures':[[1.,0.],[0.,1.],[1.,1.],[0.2,0.8]],'nodeIds':['a','b','c','d'],'edges':[[0,1],[1,2],[2,3]],'directed':False}

def test_split_deterministic():
    m=load_service(); a=m._gnn_split_plan({'itemCount':10,'seed':334}); b=m._gnn_split_plan({'itemCount':10,'seed':334}); assert a['splitIndices']==b['splitIndices']; assert a['gnnSplitPlanArtifact']['schema']==m.GNN_SPLIT_PLAN_SCHEMA

def test_node_multiclass_training_and_checkpoint_resume():
    m=load_service(); p=graph(); p.update({'seed':334,'task':'node-multiclass-classification','labels':[0,1,0,1],'modelSpec':model(m,2),'epochs':8,'learningRate':0.1,'splitIndices':{'train':[0,1,2],'validation':[3],'test':[]}})
    r=m._gnn_train(p); assert r['gnnTrainingArtifact']['epochsCompleted']==8; assert r['gnnCheckpointArtifact']['currentEpoch']==8; assert r['trainedModelSpec']['modelSpecFingerprint']!=model(m,2).get('modelSpecFingerprint')
    q=dict(p); q['checkpoint']=r['gnnCheckpointArtifact']; q['additionalEpochs']=2; q.pop('epochs',None); q.pop('modelSpec',None); rr=m._gnn_checkpoint_resume(q); assert rr['gnnCheckpointArtifact']['currentEpoch']==10

def test_graph_binary_training():
    m=load_service(); g1=graph(); g2=graph(); g1['label']=0; g2['label']=1; p={'seed':334,'task':'graph-binary-classification','graphs':[g1,g2],'modelSpec':model(m,1),'epochs':2,'learningRate':0.05,'splitIndices':{'train':[0,1],'validation':[],'test':[]}}
    r=m._gnn_train(p); assert r['gnnTrainingArtifact']['task']=='graph-binary-classification'

def test_link_training_requires_explicit_examples():
    m=load_service(); p=graph(); p.update({'seed':334,'task':'link-prediction','modelSpec':model(m,2),'epochs':2,'learningRate':0.05,'linkExamples':[{'source':0,'target':1,'label':1},{'source':0,'target':3,'label':0}], 'splitIndices':{'train':[0,1],'validation':[],'test':[]}})
    r=m._gnn_train(p); assert r['gnnTrainingArtifact']['task']=='link-prediction'; assert r['gnnTrainingArtifact']['trainingLabelsPersisted'] is False

def test_security_and_optimizer_boundary():
    m=load_service(); p=graph(); p.update({'task':'node-binary-classification','labels':[0,1,1,0],'modelSpec':model(m,1),'epochs':1,'optimizer':'adam','splitIndices':{'train':[0,1],'validation':[],'test':[2,3]}})
    try:m._gnn_train(p); assert False
    except HTTPException as e: assert e.status_code==400
