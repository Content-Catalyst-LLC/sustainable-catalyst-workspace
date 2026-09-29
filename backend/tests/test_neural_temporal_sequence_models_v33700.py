from __future__ import annotations
import importlib.util, pathlib
from fastapi import HTTPException

def load_service():
    p=pathlib.Path(__file__).parents[1]/'neural-runtime/service.py'; spec=importlib.util.spec_from_file_location('scw_v337_service',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def seq():
    return {'featureNames':['x','y'],'timestamps':['t0','t1','t2','t3'],'sequenceTensor':[[0.1,0.2],[0.2,0.1],[0.3,0.4],[0.4,0.3]]}

def rnn(m,out=2):
    return {'schema':m.SEQUENCE_MODEL_SPEC_SCHEMA,'adapter':'tanh-rnn','inputFeatures':2,'hiddenFeatures':2,'outputFeatures':out,'inputWeights':[[0.4,0.1],[0.2,0.3]],'recurrentWeights':[[0.1,0.0],[0.0,0.1]],'hiddenBias':[0.0,0.0],'outputWeights':[[0.5,0.2] for _ in range(out)],'outputBias':[0.0]*out}

def gru(m,out=2):
    base={'schema':m.SEQUENCE_MODEL_SPEC_SCHEMA,'adapter':'gru','inputFeatures':2,'hiddenFeatures':2,'outputFeatures':out,'outputWeights':[[0.4,0.2] for _ in range(out)],'outputBias':[0.0]*out}
    for p in ('update','reset','candidate'):
        base[p+'InputWeights']=[[0.2,0.1],[0.1,0.2]]; base[p+'RecurrentWeights']=[[0.1,0.0],[0.0,0.1]]; base[p+'Bias']=[0.0,0.0]
    return base

def test_sequence_contract_windows_projection():
    m=load_service(); p=seq(); c=m._sequence_tensor_contract(p)['sequenceTensorContractArtifact']; assert c['steps']==4 and c['features']==2 and c['externalSequenceRead'] is False
    w=m._sequence_window_plan({'length':8,'windowLength':3,'horizon':2,'stride':2}); assert w['sequenceWindowPlanArtifact']['windowCount']==2 and w['windows'][1]['inputStart']==2
    d=m._sequence_dataset_project(dict(p,windowLength=2,horizon=1,stride=1)); assert d['sequenceDatasetProjectionArtifact']['windowCount']==2 and len(d['windows'][0])==2

def test_tanh_rnn_forward_and_infer():
    m=load_service(); p=dict(seq(),modelSpec=rnn(m,2)); s=m._sequence_model_summary(p); assert s['adapter']=='tanh-rnn' and s['parameterCount']>0
    f=m._sequence_forward(p); assert len(f['outputs'])==2 and len(f['hiddenState'])==2
    b=dict(seq(),modelSpec=rnn(m,1),task='binary-classification'); r=m._sequence_infer(b); assert 0 <= r['prediction']['probability'] <= 1 and r['sequencePredictionArtifact']['isObservedEvidence'] is False

def test_gru_multiclass_and_embedding():
    m=load_service(); p=dict(seq(),modelSpec=gru(m,3),task='multiclass-classification'); r=m._sequence_infer(p); assert len(r['prediction']['probabilities'])==3
    e=m._sequence_embedding_extract(dict(seq(),modelSpec=gru(m,2))); assert len(e['embedding'])==2 and e['sequenceEmbeddingArtifact']['dimensions']==2

def test_recursive_forecast():
    m=load_service(); p=dict(seq(),modelSpec=rnn(m,2),forecastHorizon=3); r=m._sequence_forecast(p); assert len(r['forecast'])==3 and r['sequenceForecastArtifact']['recursive'] is True and r['sequenceForecastArtifact']['isObservedEvidence'] is False

def test_sequence_boundaries():
    m=load_service(); p=dict(seq(),modelSpec=dict(rnn(m,2),adapter='transformer-from-url'))
    try: m._sequence_model_summary(p); assert False
    except HTTPException as e: assert e.status_code==400
    p=dict(seq(),modelSpec=rnn(m,1),forecastHorizon=2)
    try: m._sequence_forecast(p); assert False
    except HTTPException as e: assert e.status_code==400
    env={'schema':'sc-workspace-polyglot-execution-envelope/1.0','language':'neural','operation':'workspace.neural.sequence-forward','arbitraryCodeExecution':False,'payload':dict(seq(),modelSpec=rnn(m,2),sequenceUrl='https://example.invalid/data.json')}
    m.TOKEN='test-token'
    try: m.execute(env, authorization='Bearer test-token'); assert False
    except HTTPException as e: assert e.status_code==400
