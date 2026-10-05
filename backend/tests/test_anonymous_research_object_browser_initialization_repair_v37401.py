from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_v37401():
    b=(ROOT/"standalone/assets/sc-workspace-research-object-browser-v37401.js").read_text()
    s=(ROOT/"standalone/assets/workspace-standalone-shell-v37401.js").read_text()
    assert "authRequired:true" in b
    assert "try{state=await api.get('/v1/research-objects?" in b
    assert "Server-backed research objects require a signed-in Workspace session." in s
    assert "workspaceVersion: '3.74.0.1'" in (ROOT/"standalone/config.js").read_text()
