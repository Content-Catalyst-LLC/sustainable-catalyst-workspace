"""Synthetic scientific continuity checks layered over recovery_validation.
Does not implement trusted identity, authorization, storage, or scientific peer review.
"""
from dataclasses import dataclass
from typing import Tuple
from recovery_validation import Snapshot, RecoveryError, compare_recovery

@dataclass(frozen=True)
class ScientificLink:
    artifact_id: str
    artifact_revision: int
    source_id: str
    source_revision: str
    method_id: str
    method_revision: str
    output_id: str
    output_digest: str
    evidence_class: str   # observed, modeled, derived
    review_state: str     # unreviewed, reviewed
    visibility: str       # private, public

CLASSES = {'observed', 'modeled', 'derived'}
REVIEWS = {'unreviewed', 'reviewed'}
VISIBILITY = {'private', 'public'}

def _digest(value: str) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False

def validate_links(snapshot: Snapshot, links: Tuple[ScientificLink, ...]) -> dict:
    artifacts = {a.artifact_id: a for a in snapshot.artifacts}
    pairs = set()
    for link in links:
        identity = (link.artifact_id, link.artifact_revision, link.output_id)
        if identity in pairs:
            raise RecoveryError('duplicate_scientific_link')
        pairs.add(identity)
        artifact = artifacts.get(link.artifact_id)
        if artifact is None or artifact.revision != link.artifact_revision:
            raise RecoveryError('scientific_artifact_revision_mismatch')
        if not all([link.source_id, link.source_revision, link.method_id,
                    link.method_revision, link.output_id]):
            raise RecoveryError('missing_scientific_provenance')
        if not _digest(link.output_digest):
            raise RecoveryError('invalid_output_digest')
        if link.evidence_class not in CLASSES or link.review_state not in REVIEWS or link.visibility not in VISIBILITY:
            raise RecoveryError('invalid_scientific_classification')
        if link.visibility == 'public' and (artifact.status != 'published' or link.review_state != 'reviewed'):
            raise RecoveryError('unreviewed_or_unpublished_public_link')
    return {'ok': True, 'scientific_link_count': len(links)}

def verify_scientific_recovery(before: Snapshot, after: Snapshot,
                               before_links: Tuple[ScientificLink, ...],
                               after_links: Tuple[ScientificLink, ...], tenant_id: str) -> dict:
    base = compare_recovery(before, after, tenant_id)
    validate_links(before, before_links)
    validate_links(after, after_links)
    after_map = {(x.artifact_id, x.artifact_revision, x.output_id): x for x in after_links}
    for link in before_links:
        artifact = next(a for a in before.artifacts if a.artifact_id == link.artifact_id)
        if artifact.status in {'accepted', 'published'}:
            restored = after_map.get((link.artifact_id, link.artifact_revision, link.output_id))
            if restored is None:
                raise RecoveryError('accepted_scientific_lineage_missing')
            if restored != link:
                raise RecoveryError('accepted_scientific_lineage_changed')
    base['scientific_lineage_preserved'] = True
    base['scientific_links_checked'] = len(before_links)
    return base
