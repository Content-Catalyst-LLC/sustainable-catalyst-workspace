from fastapi.testclient import TestClient
from app.main import app
from app.frontend_runtime import profile

def test_profile_reduces_browser_authority():
    p=profile()
    assert p["workspaceVersion"]=="2.36.0"
    assert p["backendAuthoritative"] is True and p["browserAuthoritativeState"] is False
    assert p["legacyCompatibilityMode"]=="lazy-browser-local-only"
    assert p["historicalVersionedFrontendAssetsRetired"] is True
    assert "canonical-state" in p["forbiddenBrowserAuthorities"]

def test_health_advertises_frontend_reduction():
    d=TestClient(app).get('/health').json()
    assert d['version']=='2.36.0'
    assert d['frontendLogicReductionLegacyJsRetirement'] is True
    assert d['frontendPrimaryShellThin'] is True
    assert d['packageAssetNamesVersionDerived'] is True

def test_frontend_runtime_endpoint_is_protected():
    r=TestClient(app).get('/v1/frontend-runtime')
    assert r.status_code in (401,503)
