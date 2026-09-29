from __future__ import annotations
import importlib.util, pathlib
from fastapi import HTTPException
P=pathlib.Path(__file__).resolve().parents[1]/"neural-runtime"/"service.py"
spec=importlib.util.spec_from_file_location("sc_neural_v33900",P); s=importlib.util.module_from_spec(spec); spec.loader.exec_module(s)

def symbols():
    return [
      {"symbolId":"claim:A","symbolType":"claim-ref","label":"Claim A","sourceRef":"core:claim:A"},
      {"symbolId":"evidence:B","symbolType":"evidence-ref","label":"Evidence B","sourceRef":"core:evidence:B"},
      {"symbolId":"finding:C","symbolType":"finding-ref","label":"Finding C","sourceRef":"core:finding:C"},
    ]

def rules():
    return [
      {"ruleId":"r1","operator":"implies","leftSymbolId":"claim:A","rightSymbolId":"evidence:B"},
      {"ruleId":"r2","operator":"requires","leftSymbolId":"evidence:B","rightSymbolId":"finding:C"},
    ]

def test_health_and_registry():
    h=s.health(); assert h["version"] in {"3.39.0","3.40.0"}; assert len(h["operations"])>=101; assert h["neuralSymbolicResearchIntelligenceRuntime"] is True; assert h["neuralSymbolicTruthAdjudicationEnabled"] is False

def test_symbol_context_binding():
    a=s._ns_symbol_contract({"symbol":symbols()[0]})["neuralSymbolicSymbolArtifact"]; assert a["truthValueAssigned"] is False
    c=s._ns_context_project({"symbols":symbols()}); assert c["neuralSymbolicContextArtifact"]["symbolCount"]==3
    b=s._ns_bind({"symbol":symbols()[0],"embedding":[0.1,0.2,0.3],"representationRef":"workspace:embedding:1"}); assert b["neuralSymbolicBindingArtifact"]["semanticEquivalenceAsserted"] is False

def test_rules_constraints_inference_and_explanation():
    rc=s._ns_rule_contract({"rules":rules()}); assert rc["neuralSymbolicRuleSetArtifact"]["ruleCount"]==2
    bad=s._ns_constraint_evaluate({"rules":rules(),"activeSymbolIds":["claim:A"]}); assert bad["neuralSymbolicConstraintArtifact"]["validUnderDeclaredRules"] is False
    inf=s._ns_infer({"rules":rules(),"activeSymbolIds":["claim:A"]}); assert inf["inferredSymbolIds"]==["evidence:B"] and inf["neuralSymbolicInferenceArtifact"]["truthValueAssigned"] is False
    ex=s._ns_explain({"inferenceArtifact":inf["neuralSymbolicInferenceArtifact"]}); assert ex["neuralSymbolicExplanationArtifact"]["reasonCount"]==1

def test_relation_scoring():
    r=s._ns_relation_score({"leftEmbedding":[1.0,0.0],"rightEmbedding":[1.0,0.0],"metric":"cosine","relationType":"representation-affinity"}); assert abs(r["value"]-1.0)<1e-6; assert r["neuralSymbolicRelationArtifact"]["isObservedEvidence"] is False

def test_security_and_epistemic_boundaries():
    try: s._ns_rule_contract({"rules":[{"ruleId":"x","operator":"eval","leftSymbolId":"a","rightSymbolId":"b"}]}); raise AssertionError("unsupported operator should fail")
    except HTTPException: pass
    assert "knowledgeBaseUrl" in s.BLOCKED_PAYLOAD_KEYS and "ruleEngineUrl" in s.BLOCKED_PAYLOAD_KEYS
    source=P.read_text(); assert "torch.load(" not in source and "torch.save(" not in source and "ruleEngineUrl" in source and "NEURAL_SYMBOLIC_RULE_OPERATORS" in source
