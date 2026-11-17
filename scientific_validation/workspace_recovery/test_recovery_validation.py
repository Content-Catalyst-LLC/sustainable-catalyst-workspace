import unittest
from dataclasses import replace
from recovery_validation import Artifact, Event, Snapshot, RecoveryError, verify_snapshot, compare_recovery

DIGEST = 'a' * 64
TIME = '2026-01-01T12:00:00Z'

def fixture(status='accepted'):
    events = (Event('ev1','doc1',1,None,'owner','2026-01-01T10:00:00Z','create'), Event('ev2','doc1',2,1,'reviewer','2026-01-01T11:00:00Z','accept'))
    if status == 'published':
        events += (Event('ev3','doc1',3,2,'publisher','2026-01-01T11:30:00Z','publish'),)
    return Snapshot('proj1','tenant1',TIME,(Artifact('doc1',len(events),status,DIGEST),),events)

class RecoveryTests(unittest.TestCase):
    def test_valid(self): self.assertTrue(verify_snapshot(fixture(), 'tenant1')['ok'])
    def test_compare_same(self): self.assertTrue(compare_recovery(fixture(),fixture(),'tenant1')['ok'])
    def test_published(self): self.assertTrue(verify_snapshot(fixture('published'),'tenant1')['ok'])
    def test_tenant_boundary(self):
        with self.assertRaisesRegex(RecoveryError,'tenant_mismatch'): verify_snapshot(fixture(),'tenant2')
    def test_missing_project(self):
        with self.assertRaisesRegex(RecoveryError,'missing_scope'): verify_snapshot(replace(fixture(),project_id=''),'tenant1')
    def test_invalid_timestamp(self):
        with self.assertRaisesRegex(RecoveryError,'invalid_timestamp'): verify_snapshot(replace(fixture(),captured_at='bad'),'tenant1')
    def test_duplicate_artifact(self):
        x=fixture()
        with self.assertRaisesRegex(RecoveryError,'invalid_or_duplicate_artifact'): verify_snapshot(replace(x,artifacts=x.artifacts+x.artifacts),'tenant1')
    def test_invalid_digest(self):
        x=fixture()
        with self.assertRaisesRegex(RecoveryError,'invalid_artifact'): verify_snapshot(replace(x,artifacts=(replace(x.artifacts[0],digest='x'),)),'tenant1')
    def test_duplicate_event(self):
        x=fixture()
        with self.assertRaisesRegex(RecoveryError,'duplicate_or_missing_event_id'): verify_snapshot(replace(x,events=x.events+(x.events[0],)),'tenant1')
    def test_orphan_event(self):
        x=fixture()
        with self.assertRaisesRegex(RecoveryError,'orphan_event'): verify_snapshot(replace(x,events=x.events+(replace(x.events[0],event_id='ev3',artifact_id='ghost'),)),'tenant1')
    def test_revision_gap(self):
        x=fixture()
        with self.assertRaisesRegex(RecoveryError,'revision_gap'): verify_snapshot(replace(x,events=(x.events[0],)),'tenant1')
    def test_wrong_parent(self):
        x=fixture()
        with self.assertRaisesRegex(RecoveryError,'broken_revision_lineage'): verify_snapshot(replace(x,events=(x.events[0],replace(x.events[1],parent_revision=None))),'tenant1')
    def test_acceptance_missing(self):
        x=fixture()
        with self.assertRaisesRegex(RecoveryError,'acceptance_event_missing'): verify_snapshot(replace(x,events=(x.events[0],replace(x.events[1],kind='edit'))),'tenant1')
    def test_publication_event_missing(self):
        x=fixture('published')
        with self.assertRaisesRegex(RecoveryError,'publication_event_missing'): verify_snapshot(replace(x,events=x.events[:-1]+(replace(x.events[-1],kind='edit'),)),'tenant1')
    def test_future_event(self):
        x=fixture()
        with self.assertRaisesRegex(RecoveryError,'event_after_snapshot'): verify_snapshot(replace(x,events=(replace(x.events[0],occurred_at='2027-01-01T00:00:00Z'),x.events[1])),'tenant1')
    def test_accepted_artifact_lost(self):
        x=fixture()
        with self.assertRaisesRegex(RecoveryError,'accepted_artifact_missing'): compare_recovery(x,replace(x,artifacts=(),events=()),'tenant1')
    def test_accepted_digest_changed(self):
        x=fixture()
        y=replace(x,artifacts=(replace(x.artifacts[0],digest='b'*64),))
        with self.assertRaisesRegex(RecoveryError,'accepted_digest_changed'): compare_recovery(x,y,'tenant1')
    def test_audit_event_missing(self):
        # restore has a valid, newly created history with alternate event ID
        x=fixture()
        y=replace(x,events=(replace(x.events[0],event_id='different'),x.events[1]))
        with self.assertRaisesRegex(RecoveryError,'audit_event_missing'): compare_recovery(x,y,'tenant1')
    def test_project_mismatch(self):
        x=fixture()
        with self.assertRaisesRegex(RecoveryError,'project_mismatch'): compare_recovery(x,replace(x,project_id='proj2'),'tenant1')

if __name__=='__main__': unittest.main()
