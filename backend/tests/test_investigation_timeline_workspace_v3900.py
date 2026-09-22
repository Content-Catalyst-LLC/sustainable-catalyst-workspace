from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.client_contracts import TYPED_ENDPOINTS
from app.investigation_timeline_workspace import (
    InvestigationEventRelationRequest,
    InvestigationEventRequest,
    TIMELINE_WORKSPACE_SCHEMA,
    profile,
)
from app.main import app


def test_profile_boundaries():
    p = profile()
    assert p["workspaceVersion"] == "3.9.0"
    assert p["schema"] == TIMELINE_WORKSPACE_SCHEMA
    assert p["automaticCausalityInference"] is False
    assert p["automaticMotiveInference"] is False
    assert p["automaticCulpabilityInference"] is False
    assert p["automaticNarrativeSelection"] is False
    assert p["automaticTruthDetermination"] is False
    assert p["automaticEvidenceRanking"] is False


def test_typed_operations_present():
    expected = {
        "investigationTimelineWorkspace",
        "investigationEventStore",
        "investigationEvents",
        "investigationEvent",
        "investigationEventRevisions",
        "investigationEventStatementLinkCreate",
        "investigationEventStatementLinks",
        "investigationEventRelationCreate",
        "investigationEventRelations",
        "investigationTimeline",
        "investigationReconstructionGraph",
        "investigationTemporalDiagnostics",
        "investigationTimelineSnapshotCreate",
        "investigationTimelineSnapshots",
    }
    assert expected <= set(TYPED_ENDPOINTS)


def test_openapi_operations_present():
    paths = app.openapi()["paths"]
    for name, endpoint in TYPED_ENDPOINTS.items():
        if name.startswith("investigationTimeline") or name.startswith("investigationEvent") or name in {
            "investigationReconstructionGraph",
            "investigationTemporalDiagnostics",
        }:
            assert endpoint["path"] in paths
            assert endpoint["method"].lower() in paths[endpoint["path"]]


def test_event_and_relation_validation():
    with pytest.raises(ValidationError):
        InvestigationEventRequest(
            schema="sc-workspace-investigation-event-request/1.0",
            projectId="p-1",
            title="Impossible range",
            startAt=datetime(2026, 1, 2, tzinfo=timezone.utc),
            endAt=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    with pytest.raises(ValidationError):
        InvestigationEventRelationRequest(
            schema="sc-workspace-investigation-event-relation-request/1.0",
            projectId="p-1",
            fromEventId="event-a",
            toEventId="event-a",
            relation="precedes",
        )


def test_release_lineage():
    from app.config import get_settings
    assert get_settings().service_version == "3.9.1"
