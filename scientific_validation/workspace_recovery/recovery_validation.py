"""Synthetic, pure-reference validation of Workspace recovery snapshots.
Not a Workspace production API or a substitute for database reconciliation.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Tuple

class RecoveryError(ValueError):
    pass

@dataclass(frozen=True)
class Event:
    event_id: str
    artifact_id: str
    revision: int
    parent_revision: int | None
    actor_id: str
    occurred_at: str
    kind: str

@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    revision: int
    status: str  # draft, reviewed, accepted, published
    digest: str

@dataclass(frozen=True)
class Snapshot:
    project_id: str
    tenant_id: str
    captured_at: str
    artifacts: Tuple[Artifact, ...]
    events: Tuple[Event, ...]

STATUSES = {'draft', 'reviewed', 'accepted', 'published'}

def _timestamp(raw: str) -> datetime:
    try:
        result = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        if result.tzinfo is None:
            raise ValueError('missing timezone')
        return result.astimezone(timezone.utc)
    except (TypeError, ValueError) as exc:
        raise RecoveryError('invalid_timestamp') from exc

def verify_snapshot(snapshot: Snapshot, tenant_id: str) -> dict:
    if not snapshot.project_id or not snapshot.tenant_id:
        raise RecoveryError('missing_scope')
    if snapshot.tenant_id != tenant_id:
        raise RecoveryError('tenant_mismatch')
    captured = _timestamp(snapshot.captured_at)
    artifacts = {}
    for artifact in snapshot.artifacts:
        if not artifact.artifact_id or artifact.artifact_id in artifacts:
            raise RecoveryError('invalid_or_duplicate_artifact')
        if artifact.revision < 1 or artifact.status not in STATUSES or len(artifact.digest) != 64:
            raise RecoveryError('invalid_artifact')
        try:
            int(artifact.digest, 16)
        except ValueError as exc:
            raise RecoveryError('invalid_digest') from exc
        artifacts[artifact.artifact_id] = artifact
    event_ids = set()
    events_by_artifact = {aid: [] for aid in artifacts}
    for event in snapshot.events:
        if not event.event_id or event.event_id in event_ids:
            raise RecoveryError('duplicate_or_missing_event_id')
        event_ids.add(event.event_id)
        if event.artifact_id not in artifacts:
            raise RecoveryError('orphan_event')
        if not event.actor_id or not event.kind:
            raise RecoveryError('incomplete_event')
        if _timestamp(event.occurred_at) > captured:
            raise RecoveryError('event_after_snapshot')
        events_by_artifact[event.artifact_id].append(event)
    for artifact_id, artifact in artifacts.items():
        events = sorted(events_by_artifact[artifact_id], key=lambda e: e.revision)
        if len(events) != artifact.revision:
            raise RecoveryError('revision_gap')
        for index, event in enumerate(events, start=1):
            if event.revision != index or event.parent_revision != (index - 1 if index > 1 else None):
                raise RecoveryError('broken_revision_lineage')
        if artifact.status in {'accepted', 'published'} and not any(e.kind == 'accept' for e in events):
            raise RecoveryError('acceptance_event_missing')
        if artifact.status == 'published' and events[-1].kind != 'publish':
            raise RecoveryError('publication_event_missing')
    return {'ok': True, 'project_id': snapshot.project_id, 'artifact_count': len(artifacts), 'event_count': len(event_ids)}

def compare_recovery(pre_failure: Snapshot, recovered: Snapshot, tenant_id: str) -> dict:
    verify_snapshot(pre_failure, tenant_id)
    verify_snapshot(recovered, tenant_id)
    if pre_failure.project_id != recovered.project_id:
        raise RecoveryError('project_mismatch')
    before = {a.artifact_id: a for a in pre_failure.artifacts}
    after = {a.artifact_id: a for a in recovered.artifacts}
    for key, original in before.items():
        if original.status in {'accepted', 'published'}:
            current = after.get(key)
            if current is None:
                raise RecoveryError('accepted_artifact_missing')
            if current.revision < original.revision:
                raise RecoveryError('accepted_revision_regressed')
            if current.revision == original.revision and current.digest != original.digest:
                raise RecoveryError('accepted_digest_changed')
    orig_event_ids = {e.event_id for e in pre_failure.events}
    restored_event_ids = {e.event_id for e in recovered.events}
    if not orig_event_ids.issubset(restored_event_ids):
        raise RecoveryError('audit_event_missing')
    return {'ok': True, 'accepted_preserved': True, 'events_preserved': True}
