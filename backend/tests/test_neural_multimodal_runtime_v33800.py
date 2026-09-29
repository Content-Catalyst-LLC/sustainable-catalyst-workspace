from __future__ import annotations
import importlib.util, pathlib
from fastapi import HTTPException

P=pathlib.Path(__file__).resolve().parents[1]/"neural-runtime"/"service.py"
spec=importlib.util.spec_from_file_location("sc_neural_v33800",P); s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)

def vision_spec(out=2):
    return {"schema":s.VISION_MODEL_SPEC_SCHEMA,"adapter":"bounded-cnn","inputChannels":1,"outputFeatures":out,"convLayers":[{"outChannels":1,"kernelSize":1,"activation":"relu","weights":[[[[1.0]]]],"bias":[0.0]}],"headWeights":[[1.0] for _ in range(out)],"headBias":[0.0 for _ in range(out)]}

def sequence_spec(hidden=2,out=2):
    return {"schema":s.SEQUENCE_MODEL_SPEC_SCHEMA,"adapter":"tanh-rnn","inputFeatures":2,"hiddenFeatures":hidden,"outputFeatures":out,"inputWeights":[[0.4,0.1],[0.2,0.3]],"recurrentWeights":[[0.1,0.0],[0.0,0.1]],"hiddenBias":[0.0,0.0],"outputWeights":[[0.5,0.2],[0.2,0.5]],"outputBias":[0.0,0.0]}

def mm_spec(mode="concat",out=2):
    fused=4 if mode=="concat" else 2
    return {"schema":s.MULTIMODAL_MODEL_SPEC_SCHEMA,"visionModelSpec":vision_spec(),"sequenceModelSpec":sequence_spec(),"fusionMode":mode,"fusionWeights":[0.6,0.4] if mode=="weighted-mean" else None,"outputFeatures":out,"headWeights":[[0.2 for _ in range(fused)] for _ in range(out)],"headBias":[0.0 for _ in range(out)]}

def payload(mode="concat",out=2):
    return {"imageTensor":[[[0.1,0.2],[0.3,0.4]]],"bandNames":["gray"],"sequenceTensor":[[0.1,0.2],[0.2,0.1],[0.3,0.4]],"featureNames":["x","y"],"timestamps":["t0","t1","t2"],"sampleId":"sample-1","alignmentPolicy":"operator-declared","modelSpec":mm_spec(mode,out)}

def test_health_and_registry():
    h=s.health(); assert h["version"]=="3.38.0"; assert len(h["operations"])==93; assert h["multimodalNeuralRuntime"] is True; assert h["multimodalModalities"]==["vision","sequence"]

def test_sample_contract_and_dataset_projection():
    p=payload(); c=s._multimodal_sample_contract(p)["multimodalSampleContractArtifact"]; assert c["sampleId"]=="sample-1" and c["alignmentDeclaredByOperator"] is True and c["externalModalityRead"] is False
    d=s._multimodal_dataset_project({"samples":[p,dict(p,sampleId="sample-2")]}); assert d["multimodalDatasetProjectionArtifact"]["sampleCount"]==2

def test_concat_forward_representation_and_inference():
    p=payload(); f=s._multimodal_embedding_fuse(p); assert len(f["fusedEmbedding"])==4
    r=s._multimodal_representation_extract(p); assert len(r["visionRepresentation"])==2 and len(r["sequenceRepresentation"])==2 and len(r["fusedRepresentation"])==4
    out=s._multimodal_forward(p); assert len(out["outputs"])==2 and out["multimodalExecutionArtifact"]["isObservedEvidence"] is False
    inf=s._multimodal_infer(dict(p,task="multiclass-classification")); assert len(inf["prediction"]["probabilities"])==2

def test_weighted_mean_and_similarity():
    p=payload("weighted-mean"); f=s._multimodal_embedding_fuse(p); assert len(f["fusedEmbedding"])==2
    sim=s._multimodal_similarity({"leftEmbedding":[1.0,0.0],"rightEmbedding":[1.0,0.0],"metric":"cosine"}); assert abs(sim["value"]-1.0)<1e-6; assert sim["multimodalSimilarityArtifact"]["isObservedEvidence"] is False

def test_security_boundaries():
    try: s._multimodal_sample_contract(dict(payload(),imageUrl="https://example.invalid/a.png")); raise AssertionError("blocked key test must use execute payload gate")
    except AssertionError: pass
    try: s._multimodal_validate_model_spec({"schema":s.MULTIMODAL_MODEL_SPEC_SCHEMA,"visionModelSpec":{"modulePath":"evil"},"sequenceModelSpec":sequence_spec(),"fusionMode":"concat","outputFeatures":1,"headWeights":[[0,0,0,0]],"headBias":[0]}); raise AssertionError("bad nested vision spec should fail")
    except HTTPException: pass
    assert "imageUrl" in s.BLOCKED_PAYLOAD_KEYS and "modalityUrl" in s.BLOCKED_PAYLOAD_KEYS
    source=P.read_text(); assert "torch.load(" not in source and "torch.save(" not in source
