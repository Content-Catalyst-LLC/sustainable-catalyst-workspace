from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def test_manifest():
    m=json.loads((ROOT/"release-manifest-v0.1.0.json").read_text())
    assert m["version"]=="0.1.0"
    assert m["access_model"]=="free-public"
    assert m["registry"]["family"]=="commercial"

def test_registry_record():
    r=json.loads((ROOT/"registry/workspace-product-record-v0.1.0.json").read_text())
    assert r["canonical_id"]=="sustainable-catalyst-workspace"
    assert r["console_screen"]=="commercial"
    assert r["commercial"]=="1"
    assert r["public_interest"]=="1"

def test_persistence_boundary():
    js=(ROOT/"wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.1.0.js").read_text()
    assert "localStorage" in js
    php=(ROOT/"wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php").read_text()
    assert "server_project_storage' => false" in php
