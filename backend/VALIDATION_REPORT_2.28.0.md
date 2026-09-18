# Validation Report — Workspace v2.28.0

## Release
Declarative Visualization Specification API

## Source release gates
- Backend regression: 101/101 passed.
- Visualization/backend-authority/orchestration/study targeted set: 29/29 passed.
- v2.28 release-contract validator: PASS.
- WordPress PHP syntax: 31/31 files passed.
- JavaScript syntax: PASS.
- Python compile: PASS.
- Docker Compose structural validation: 12 services.
- VPS deployer shell syntax: PASS.
- Deployer health assertion: exactly 2.28.0.
- Migration 028 included and visualization registry privilege checks present.
- v2.27 `.env` is an explicit upgrade source for the v2.28 deployer.
- Renderer-specific executable fields and arbitrary-code execution remain disabled.

## Visualization contract
- 13 bounded renderer-neutral view types.
- Single, grid, and dashboard scene layouts.
- Explicit filter/highlight/select linked-view semantics.
- Artifact/dataset/execution-run/receipt provenance source pinning plus bounded inline rows.
- Deterministic SHA-256 specification fingerprints.
- Revision history and durable create/update/delete receipts.
- Reproducible scientific study packages now include visualization specifications.
- Full repaired Workspace interface asset lineage preserved (~872 KB JS / ~349 KB CSS).

## Packaged-artifact replay
- Packaged backend ZIP regression: 101/101 passed.
- Packaged WordPress ZIP: 31/31 PHP files plus JavaScript syntax passed.
- ZIP integrity: backend, repository, WordPress, tiny patch, and release bundle all passed.
- Component SHA-256 verification: PASS.
- Tiny-patch byte replay: 36/36 changed/new files exact.

## Package closure
- Incremental changed/new files from v2.27.0: 36.
- No files deleted from the v2.27 baseline.
- The deployer explicitly carries the v2.27 `.env` forward, applies migration 028, asserts health version 2.28.0, and performs a live renderer-neutral visualization-spec smoke test.
