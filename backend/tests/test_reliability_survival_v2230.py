import importlib.util, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("reliability_service",ROOT/"reliability-runtime/service.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
def run(op,p): return mod.execute(op,p)

def test_kaplan_meier_censoring():
    r=run("workspace.reliability.kaplan-meier",{"times":[1,2,2,3],"events":[1,1,0,1]})
    assert r["sampleCount"]==4 and r["eventCount"]==3 and len(r["survivalTable"])==3

def test_exponential_fit():
    r=run("workspace.reliability.exponential-fit",{"times":[10,20,30,40],"events":[1,1,1,1],"horizon":25})
    assert abs(r["metrics"]["failureRate"]-0.04)<1e-12 and 0<r["metrics"]["reliabilityAtHorizon"]<1

def test_weibull_fit_and_at_time():
    r=run("workspace.reliability.weibull-fit",{"times":[10,15,22,31,45],"events":[1,1,1,1,1]})
    assert r["metrics"]["shape"]>0 and r["metrics"]["scale"]>0
    q=run("workspace.reliability.reliability-at-time",{"model":"weibull","shape":2,"scale":100,"time":100})
    assert abs(q["metrics"]["reliability"]-math.exp(-1))<1e-12

def test_system_reliability_and_availability():
    r=run("workspace.reliability.series-parallel-system",{"groups":[{"kind":"parallel","reliabilities":[0.9,0.9]},{"kind":"series","reliabilities":[0.8]}],"systemKind":"series"})
    assert abs(r["metrics"]["systemReliability"]-0.792)<1e-12
    a=run("workspace.reliability.repairable-availability",{"mtbf":100,"mttr":4})
    assert abs(a["metrics"]["availability"]-(100/104))<1e-12

def test_binomial_interval_and_inverse_power():
    b=run("workspace.reliability.binomial-reliability",{"successes":95,"trials":100})
    assert b["metrics"]["interval"]["lower"]<0.95<b["metrics"]["interval"]["upper"]
    r=run("workspace.reliability.inverse-power-life",{"stresses":[1,2,4,8],"lives":[1000,500,250,125],"targetStress":16})
    assert abs(r["metrics"]["exponent"]-1)<1e-10 and abs(r["metrics"]["predictedLife"]-62.5)<1e-8

def test_health_registry_contract():
    h=mod.health(); assert h["version"]=="2.23.0" and len(h["operations"])==8 and h["arbitraryCodeExecution"] is False
