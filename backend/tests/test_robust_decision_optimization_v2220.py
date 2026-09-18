import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("decision_service",ROOT/"decision-runtime/service.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def run(op,p): return mod.execute(op,p)

def test_pareto_front():
    r=run("workspace.decision.pareto-front",{"candidates":[{"id":"A","metrics":{"benefit":10,"cost":5}},{"id":"B","metrics":{"benefit":8,"cost":7}},{"id":"C","metrics":{"benefit":11,"cost":8}}],"directions":{"benefit":"maximize","cost":"minimize"}})
    assert set(r["paretoFront"])=={"A","C"}

def test_expected_utility_rank():
    r=run("workspace.decision.expected-utility-rank",{"candidates":[{"id":"A","metrics":{"benefit":10,"cost":3}},{"id":"B","metrics":{"benefit":8,"cost":8}}],"directions":{"benefit":"maximize","cost":"minimize"},"weights":{"benefit":0.6,"cost":0.4}})
    assert r["selectedAlternative"]=="A"

def test_minimax_regret():
    p={"candidates":[{"id":"A","scores":[10,2]},{"id":"B","scores":[7,7]}],"scenarios":[{"id":"s1","probability":0.5},{"id":"s2","probability":0.5}],"direction":"maximize"}
    r=run("workspace.decision.minimax-regret",p)
    assert r["selectedAlternative"]=="B" and r["summary"]["ranking"][0]["maxRegret"]==3

def test_value_of_information():
    p={"candidates":[{"id":"A","scores":[10,0]},{"id":"B","scores":[5,5]}],"scenarios":[{"id":"s1","probability":0.5},{"id":"s2","probability":0.5}],"direction":"maximize"}
    r=run("workspace.decision.value-of-perfect-information",p)
    assert r["summary"]["evpi"]==2.5

def test_health_registry_contract():
    h=mod.health(); assert h["version"]=="2.22.0" and len(h["operations"])==8 and h["arbitraryCodeExecution"] is False
