# Workspace v2.30.0 Validation Report

## Source validation

- Full backend regression suite: **112/112 passed**.
- Targeted backend thin-state + typed-contract suite: **11/11 passed**.
- Targeted frontend thin-state + typed-client + interaction-regression suite: **17/17 passed**.
- WordPress PHP syntax: **31/31 files passed**.
- Strict TypeScript compilation: passed.
- OpenAPI → TypeScript generated-contract drift check: passed.
- Main Workspace JavaScript syntax: passed.
- Generated typed/thin-state runtime JavaScript syntax: passed.
- Python compileall: passed.
- VPS deployment script shell syntax: passed.

## Contract assertions

- PostgreSQL/Python canonical authority retained.
- Browser authoritative state remains false.
- Canonical cache is memory-only and rehydratable.
- Browser-persistent state is restricted to the transient allowlist.
- Canonical mutations are command-API-only.
- Canonical reads are server-read-model-only.
- Offline cache is explicitly non-authoritative.
- v2.28.1 interaction repair remains loaded.
- v2.29 same-origin WordPress typed proxy remains credential-safe.
- No migration 030; schema lineage remains through migration 028.
- Arbitrary-code execution remains disabled.

Historical top-level release tests intentionally encode old release identities and are not part of the v2.30 current-release gate; the current frontend regression gate is the targeted v2.30 + preserved v2.28.1/v2.29 contract set above.

## Packaged-artifact replay

- Backend ZIP test replay: **112/112 passed**.
- WordPress ZIP PHP syntax replay: **31/31 files passed**.
- Packaged typed/thin-state runtime JavaScript syntax: passed.
- Packaged main Workspace JavaScript syntax: passed.
- Backend deployment script shell syntax: passed.
- All five ZIP archives: integrity passed.
- Component SHA-256 file: all entries verified.
- v2.29.0 → v2.30.0 tiny patch reconstruction: **exact**, with **42 changed/new files** and **3 removed superseded assets**.
