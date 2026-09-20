# Workspace v2.32.0 Validation Report

Release: **Unified Scientific Object API**

Source validation gates:

- Backend regression: **122/122 passed**.
- Targeted v2.32 scientific-object backend tests: **5/5 passed**.
- Targeted frontend typed-client/thin-state/sync/scientific-object tests: **22/22 passed**.
- Generated OpenAPI → TypeScript contract drift check: PASS.
- Strict TypeScript compilation: PASS.
- Main Workspace JavaScript syntax: PASS.
- Typed client/scientific-object runtime JavaScript syntax: PASS.
- WordPress PHP lint: **31/31 files passed**.
- VPS deployer shell syntax: PASS.

Release invariants:

- PostgreSQL/Python remains canonical Workspace authority.
- Unified scientific-object projections are read-only and rehydratable.
- Ten scientific object kinds share canonical identity and fingerprint semantics.
- Revisioned kinds expose bounded revision history; execution runs expose event history.
- Provenance relationships are explicit and typed.
- Generic arbitrary scientific-object mutation is disabled.
- v2.31 local-first synchronization remains authoritative for offline draft reconciliation.
- Arbitrary code execution remains disabled.

Packaging replay must re-run backend tests from the backend ZIP, PHP/JavaScript syntax from the WordPress ZIP, contract drift, ZIP integrity/checksums, and exact v2.31.0 → v2.32.0 patch reconstruction.
