from app.utils import canonical_bytes, sha256_hex


def test_canonical_hash_is_key_order_independent():
    left = {"b": 2, "a": 1}
    right = {"a": 1, "b": 2}
    assert canonical_bytes(left) == canonical_bytes(right)
    assert sha256_hex(left) == sha256_hex(right)


def test_hash_is_sha256_hex():
    value = sha256_hex({"schema": "x", "value": 1})
    assert len(value) == 64
    int(value, 16)

from app.utils import workspace_project_fingerprint


def test_workspace_project_fingerprint_uses_sync_snapshot_contract():
    project = {
        "schema": "sc-workspace-project/20.0",
        "id": "p1",
        "persistence": {"scope": "device"},
        "recentTools": ["lab"],
    }
    fp1 = workspace_project_fingerprint(project)
    fp2 = workspace_project_fingerprint({**project, "persistence": {"scope": "other"}, "recentTools": ["workbench"]})
    assert fp1 == fp2
