from __future__ import annotations
import importlib.util, pathlib
from fastapi import HTTPException

def load_service():
    p=pathlib.Path(__file__).parents[1]/'neural-runtime/service.py'; spec=importlib.util.spec_from_file_location('scw_v336_service',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def image():
    return {'sceneId':'scene-a','crs':'EPSG:4326','bbox':[-90,38,-89,39],'bandNames':['red','green','nir','swir1','swir2'],'imageTensor':[
        [[0.2,0.3],[0.4,0.5]], [[0.3,0.4],[0.5,0.6]], [[0.6,0.7],[0.8,0.9]], [[0.4,0.4],[0.5,0.5]], [[0.2,0.3],[0.3,0.4]]
    ]}

def model(m,out=3):
    weights=[]
    for oc in range(2):
        ocw=[]
        for ic in range(5): ocw.append([[0.1*(oc+1)*(ic+1)]])
        weights.append(ocw)
    return {'schema':m.VISION_MODEL_SPEC_SCHEMA,'adapter':'bounded-cnn','inputChannels':5,'outputFeatures':out,'convLayers':[{'outChannels':2,'kernelSize':1,'activation':'relu','weights':weights,'bias':[0.0,0.0]}],'headWeights':[[0.2,0.1] for _ in range(out)],'headBias':[0.0]*out}

def test_tensor_contract_and_dataset_projection():
    m=load_service(); p=image(); r=m._vision_tensor_contract(p); assert r['visionTensorContractArtifact']['channels']==5
    d=m._vision_dataset_project({'scenes':[p,dict(p,sceneId='scene-b')]}); assert d['visionDatasetProjectionArtifact']['sceneCount']==2

def test_model_forward_and_multiclass_infer():
    m=load_service(); p=image(); p['modelSpec']=model(m,3); s=m._vision_model_summary(p); assert s['parameterCount']>0
    f=m._vision_forward(p); assert len(f['outputs'])==3
    p['task']='multiclass-classification'; r=m._vision_infer(p); assert len(r['prediction']['probabilities'])==3 and r['visionPredictionArtifact']['isObservedEvidence'] is False

def test_deterministic_tile_plan():
    m=load_service(); r=m._vision_tile_plan({'height':10,'width':12,'tileHeight':6,'tileWidth':6,'overlapHeight':2,'overlapWidth':2}); assert r['visionTilePlanArtifact']['tileCount']==6; assert r['windows'][-1]['x']==6 and r['windows'][-1]['y']==4

def test_remote_sensing_band_projection_and_ndvi():
    m=load_service(); p=image(); q=dict(p,selectBands=['nir','red']); r=m._remote_sensing_band_project(q); assert r['bandNames']==['nir','red'] and len(r['imageTensor'])==2
    n=dict(p,index='ndvi'); v=m._remote_sensing_index_compute(n); assert v['remoteSensingIndexArtifact']['index']=='ndvi'; assert v['statistics']['validCount']==4; assert v['remoteSensingIndexArtifact']['isObservedEvidence'] is False

def test_boundaries():
    m=load_service(); p=image(); p['modelSpec']=dict(model(m,2),adapter='torchvision-resnet')
    try: m._vision_model_summary(p); assert False
    except HTTPException as e: assert e.status_code==400
    p=image(); p['index']='evi'
    try: m._remote_sensing_index_compute(p); assert False
    except HTTPException as e: assert e.status_code==400
