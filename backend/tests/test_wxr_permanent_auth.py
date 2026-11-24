import importlib.util
import json
import os
import stat
import sys
import types
from pathlib import Path

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]

# Test stub. In production the route imports the existing app.session_auth. The stub is
# installed only while the module loads, so other tests still see the real app package.
_saved = {name: sys.modules.get(name) for name in ("app", "app.session_auth")}
pkg = types.ModuleType("app")
pkg.__path__ = [str(ROOT / "app")]
sys.modules.setdefault("app", pkg)
session = types.ModuleType("app.session_auth")
session.session_payload_from_request = lambda request: {"sub": request.headers.get("x-test-subject")}
sys.modules["app.session_auth"] = session
try:
    spec = importlib.util.spec_from_file_location("_wxr_permanent_auth_under_test", ROOT / "app" / "wxr_permanent_auth.py",
                                                  submodule_search_locations=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "app"
    spec.loader.exec_module(mod)
finally:
    for name, previous in _saved.items():
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous


def policy_file(tmp_path, sub="owner-1", **changes):
    import hashlib
    policy = {
        "schema": mod.POLICY_SCHEMA,
        "enabled": True,
        "project_id": mod.PROJECT_ID,
        "subject_sha256": hashlib.sha256(sub.encode()).hexdigest(),
        "approved_by": "production administrator",
        "approval_reference": "wexford-release-owner-approval",
    }
    policy.update(changes)
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy))
    path.chmod(0o600)
    return path


def call(path, subject):
    os.environ["WXR_PERMANENT_ACCESS_FILE"] = str(path)
    app = FastAPI()
    app.include_router(mod.router)
    client = TestClient(app)
    headers = {"x-test-subject": subject} if subject else {}
    return client.get("/v1/private-research/erw-access/check", headers=headers)


def test_owner_ok(tmp_path):
    response = call(policy_file(tmp_path), "owner-1")
    assert response.status_code == 204
    assert response.headers["cache-control"] == "no-store"


def test_unauthenticated_denied(tmp_path):
    assert call(policy_file(tmp_path), None).status_code == 401


def test_wrong_account_denied(tmp_path):
    assert call(policy_file(tmp_path), "owner-2").status_code == 403


def test_disabled_denied(tmp_path):
    assert call(policy_file(tmp_path, enabled=False), "owner-1").status_code == 403


def test_wrong_project_denied(tmp_path):
    assert call(policy_file(tmp_path, project_id="other-project"), "owner-1").status_code == 403


def test_world_readable_denied(tmp_path):
    path = policy_file(tmp_path)
    path.chmod(0o644)
    assert call(path, "owner-1").status_code == 403


def test_symlink_denied(tmp_path):
    path = policy_file(tmp_path)
    link = tmp_path / "policy-link.json"
    link.symlink_to(path)
    assert call(link, "owner-1").status_code == 403


def test_missing_policy_denied(tmp_path):
    assert call(tmp_path / "missing.json", "owner-1").status_code == 403


def test_wrong_hash_denied(tmp_path):
    assert call(policy_file(tmp_path, subject_sha256="not-a-hash"), "owner-1").status_code == 403
