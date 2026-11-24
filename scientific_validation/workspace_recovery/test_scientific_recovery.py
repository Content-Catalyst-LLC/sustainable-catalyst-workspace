import unittest
from dataclasses import replace
from recovery_validation import Snapshot, Artifact, Event, RecoveryError
from scientific_recovery import ScientificLink, validate_links, verify_scientific_recovery

D = 'a' * 64
DATE = '2026-11-16T20:00:00+00:00'

def fixture():
    events = (
        Event('ev1', 'report', 1, None, 'author', '2026-11-16T18:00:00+00:00', 'create'),
        Event('ev2', 'report', 2, 1, 'reviewer', '2026-11-16T19:00:00+00:00', 'accept'),
    )
    snap = Snapshot('project-synthetic', 'tenant-synthetic', DATE,
                    (Artifact('report', 2, 'accepted', D),), events)
    link = ScientificLink('report', 2, 'dataset-1', 'v1', 'method-1', 'v3',
                          'output-1', 'b'*64, 'derived', 'reviewed', 'private')
    return snap, (link,)

class ScientificContinuityTests(unittest.TestCase):
    def setUp(self):
        self.snapshot, self.links = fixture()

    def rejected(self, expected, *, snap=None, links=None, before=None, before_links=None):
        with self.assertRaisesRegex(RecoveryError, expected):
            verify_scientific_recovery(before or self.snapshot, snap or self.snapshot,
                                       before_links or self.links, links if links is not None else self.links,
                                       'tenant-synthetic')

    def test_reference_continuity_passes(self):
        result = verify_scientific_recovery(self.snapshot, self.snapshot, self.links, self.links, 'tenant-synthetic')
        self.assertTrue(result['scientific_lineage_preserved'])

    def test_empty_links_allowed_when_no_claims_registered(self):
        self.assertEqual(validate_links(self.snapshot, ())['scientific_link_count'], 0)

    def test_missing_source_id(self):
        self.rejected('missing_scientific_provenance', links=(replace(self.links[0], source_id=''),))

    def test_missing_method_revision(self):
        self.rejected('missing_scientific_provenance', links=(replace(self.links[0], method_revision=''),))

    def test_missing_output_id(self):
        self.rejected('missing_scientific_provenance', links=(replace(self.links[0], output_id=''),))

    def test_bad_output_digest(self):
        self.rejected('invalid_output_digest', links=(replace(self.links[0], output_digest='bad'),))

    def test_missing_accepted_lineage(self):
        self.rejected('accepted_scientific_lineage_missing', links=())

    def test_changed_source_revision(self):
        self.rejected('accepted_scientific_lineage_changed', links=(replace(self.links[0], source_revision='v9'),))

    def test_changed_method_revision(self):
        self.rejected('accepted_scientific_lineage_changed', links=(replace(self.links[0], method_revision='v9'),))

    def test_changed_output_digest(self):
        self.rejected('accepted_scientific_lineage_changed', links=(replace(self.links[0], output_digest='c'*64),))

    def test_duplicate_link(self):
        self.rejected('duplicate_scientific_link', links=self.links + self.links)

    def test_wrong_artifact_revision(self):
        self.rejected('scientific_artifact_revision_mismatch', links=(replace(self.links[0], artifact_revision=3),))

    def test_unknown_artifact(self):
        self.rejected('scientific_artifact_revision_mismatch', links=(replace(self.links[0], artifact_id='other'),))

    def test_invalid_evidence_class(self):
        self.rejected('invalid_scientific_classification', links=(replace(self.links[0], evidence_class='proof'),))

    def test_invalid_review_state(self):
        self.rejected('invalid_scientific_classification', links=(replace(self.links[0], review_state='certified'),))

    def test_unpublished_public_link(self):
        self.rejected('unreviewed_or_unpublished_public_link', links=(replace(self.links[0], visibility='public'),))

    def test_new_unreviewed_public_link(self):
        snap = replace(self.snapshot, artifacts=(Artifact('report', 3, 'published', D),), events=self.snapshot.events +
                       (Event('ev3', 'report', 3, 2, 'publisher', '2026-11-16T19:30:00+00:00', 'publish'),))
        with self.assertRaisesRegex(RecoveryError, 'unreviewed_or_unpublished_public_link'):
            validate_links(snap, (replace(self.links[0], artifact_revision=3, visibility='public', review_state='unreviewed'),))

    def test_wrong_tenant(self):
        with self.assertRaisesRegex(RecoveryError, 'tenant_mismatch'):
            verify_scientific_recovery(self.snapshot, self.snapshot, self.links, self.links, 'other-tenant')

    def test_artifact_digest_modified(self):
        snap = replace(self.snapshot, artifacts=(replace(self.snapshot.artifacts[0], digest='f'*64),))
        self.rejected('accepted_digest_changed', snap=snap)

    def test_event_removed(self):
        snap = replace(self.snapshot, events=self.snapshot.events[:-1])
        self.rejected('revision_gap', snap=snap)

if __name__ == '__main__':
    unittest.main()
