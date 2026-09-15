from types import SimpleNamespace

import app.polyglot as polyglot


def test_polyglot_result_uses_valid_artifact_store_contract(monkeypatch):
    captured = {}

    class FakeArtifact:
        artifact_id = "polyglot-result-job-test"
        sha256 = "a" * 64
        bytes = 123

    class FakeDb:
        def add(self, value):
            captured["receipt"] = value
        def flush(self):
            captured["flushed"] = True
        def commit(self):
            captured["committed"] = True
        def refresh(self, value):
            captured["refreshed"] = value

    def fake_get_artifact(db, user_key, artifact_id):
        captured["lookup"] = (user_key, artifact_id)
        return None

    def fake_store_artifact(db, user_key, payload):
        captured["artifact"] = payload.model_dump(by_alias=True)
        return FakeArtifact()

    monkeypatch.setattr(polyglot, "get_artifact", fake_get_artifact)
    monkeypatch.setattr(polyglot, "store_artifact", fake_store_artifact)

    row = SimpleNamespace(
        operation="workspace.polyglot.sql.aggregate",
        payload={"payload": {"rows": [{"x": 2}, {"x": 4}, {"x": 6}], "column": "x", "aggregate": "avg"}},
        user_key="wp:1",
        job_id="job-test",
        project_id="",
        request_fingerprint="b" * 64,
    )

    result = polyglot.execute_polyglot_operation(FakeDb(), row)

    assert result["polyglot"]["result"]["value"] == 4.0
    assert captured["artifact"]["schema"] == "sc-workspace-artifact-store/1.0"
    assert captured["artifact"]["artifactId"] == "polyglot-result-job-test"
    assert captured["artifact"]["expectedRevision"] == 0
    assert captured["artifact"]["mediaType"] == "application/vnd.sc.workspace.polyglot-result+json"
    assert captured["flushed"] is True
    assert captured["committed"] is True
    assert captured["refreshed"] is captured["receipt"]

