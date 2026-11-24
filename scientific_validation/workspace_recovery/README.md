# Workspace scientific recovery validation — reference package

This package extends the existing synthetic Workspace recovery validator, rather than creating an unrelated subsystem. No third-party packages are required.

## Run

```bash
python3 -m unittest -v test_recovery_validation.py test_scientific_recovery.py
```

## Verified local execution

39 tests passed (19 existing snapshot tests, 20 new scientific-lineage tests). See `test-results.txt` for executed test names and results.

## Files

- `recovery_validation.py`: previously developed snapshot/event continuity checks
- `test_recovery_validation.py`: 19 general recovery checks
- `scientific_recovery.py`: source/method/output lineage and visibility checks
- `test_scientific_recovery.py`: 20 scientific-continuity tests
- `test-results.txt`: captured test run

## Important limitations

- Digest fields are tested for syntax and continuity; this code does **not** rehash real source, manuscript, or output bytes.
- Audit events model a linear revision history, not arbitrary branch/merge DAGs.
- `review_state` and `visibility` in synthetic fixtures are untrusted labels, not genuine permissions or signed approvals.
- The implementation does not connect to Workspace, authenticate users, restore databases, perform independent numerical reproduction, or approve publication.
- Reconcile these contracts with actual schemas and release-specific tests before integration.
