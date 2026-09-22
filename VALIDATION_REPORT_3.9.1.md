# Workspace v3.9.1 Validation Report

Release engineering validation against the supplied Workspace v3.9.0 repository baseline:

- v3.9.1 Analytics R provider-promotion tests: 8/8 passed
- v3.9 timeline/event reconstruction regression tests: 5/5 passed
- combined focused regression line: 13/13 passed
- backend Python compilation: passed
- typed-client generator consistency: passed
- typed endpoints: 111
- missing OpenAPI operations: 0
- WordPress PHP syntax: passed
- v3.9.1 provider adapter JavaScript syntax: passed
- v3.9.1 typed-client JavaScript syntax: passed
- v3.9 timeline JavaScript syntax: passed
- vendored R provider: 2.2.0
- diagnostics contract: `sc.analytics-r.statistical-diagnostics-validation.v1`
- database migration: none
- migration lineage retained: 040
- production hardening contract: read-only root filesystem, UID 10001

Known Pydantic `schema` field-shadow warnings are inherited from v3.9.0 and remain non-fatal warnings.
