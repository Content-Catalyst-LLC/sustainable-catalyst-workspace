import pytest

from app.domain_authority import DomainValidationError, authority_profile, validate_domain_document, validate_notebook_document, validate_project_document


def test_authority_profile_makes_backend_canonical():
    p = authority_profile()
    assert p["mode"] == "server-authoritative"
    assert p["canonicalStore"] == "postgresql"
    assert p["backendAuthoritativeState"] is True
    assert p["browserAuthoritativeState"] is False
    assert p["clientRole"] == "presentation-interaction-local-drafts"
    assert "mutation-receipts" in p["authoritativeConcerns"]


def test_project_validation_produces_canonical_fingerprint():
    project = {
        "schema": "sc-workspace-project/20.0",
        "title": "Authority test",
        "objects": [{"id": "a", "type": "note"}, {"id": "b", "type": "dataset"}],
        "traceability": {"lineage": []},
    }
    r = validate_project_document(project)
    assert r["accepted"] is True
    assert r["objectCount"] == 2
    assert r["identifiedObjectCount"] == 2
    assert len(r["canonicalFingerprint"]) == 64


def test_project_validation_rejects_duplicate_object_ids():
    with pytest.raises(DomainValidationError) as exc:
        validate_project_document({"schema": "sc-workspace-project/20.0", "objects": [{"id": "same"}, {"id": "same"}]})
    assert exc.value.code == "duplicate-domain-id"


def test_notebook_validation_is_server_side_and_deterministic():
    notebook = {"schema": "sc-workspace-notebook/3.0", "title": "N", "cells": [{"id": "c1"}, {"id": "c2"}]}
    a = validate_notebook_document(notebook)
    b = validate_notebook_document(notebook)
    assert a["accepted"] is True
    assert a["cellCount"] == 2
    assert a["canonicalFingerprint"] == b["canonicalFingerprint"]


def test_notebook_validation_rejects_wrong_schema():
    with pytest.raises(DomainValidationError) as exc:
        validate_domain_document("notebook", {"schema": "sc-workspace-notebook/2.0"})
    assert exc.value.code == "unsupported-notebook-schema"


def test_unknown_object_kind_is_rejected():
    with pytest.raises(DomainValidationError) as exc:
        validate_domain_document("artifact", {})
    assert exc.value.code == "unsupported-domain-object-kind"
