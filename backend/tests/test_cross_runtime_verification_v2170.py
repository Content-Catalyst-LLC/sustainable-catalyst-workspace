import json
from pathlib import Path
from types import SimpleNamespace
from app.config import Settings
from app.cross_runtime_verification import _compare_json, profile_catalog

def test_version_and_profiles():
    assert Settings().service_version == "2.31.0"
    modes={x["mode"] for x in profile_catalog()}
    assert modes=={"auto","exact-digest","tolerance-aware-json"}

def test_numeric_json_tolerance_equivalence():
    a={"coef":[1.0,2.0],"metric":{"rmse":0.12500000},"label":"ok"}
    b={"coef":[1.0+1e-10,2.0-1e-10],"metric":{"rmse":0.12500001},"label":"ok"}
    ok,stats=_compare_json(a,b,1e-7,1e-6)
    assert ok is True
    assert stats["numericComparisons"]==3
    assert stats["mismatches"]==[]

def test_numeric_json_detects_divergence():
    ok,stats=_compare_json({"x":1.0},{"x":1.1},1e-9,1e-7)
    assert ok is False
    assert stats["mismatches"]

def test_release_contract_files():
    root=Path(__file__).resolve().parents[1]
    assert (root/"migrations/017_reproduction_cross_runtime_verification.sql").is_file()
    text=(root/"app/cross_runtime_verification.py").read_text()
    assert "tolerance-aware-json" in text
    assert "automaticExecution\":False" in text
    assert "arbitraryCodeExecution\":False" in text
