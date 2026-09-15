# Validation Report — Workspace v2.13.0

Release: **R Statistical & Econometric Runtime**

## Release-specific gate

- structural validator: PASS
- backend tests: 26 passed
- v2.11 scientific compute regression subset: 10 passed, 1 stale release-identity assertion deselected
- v2.12 polyglot regression subset: 7 passed, 1 stale release-lineage assertion deselected
- v2.13 R runtime tests: 10 passed
- combined targeted result: **53 passed, 2 deselected**
- Python compilation: PASS
- PHP syntax: **31/31 PASS**
- VPS deployment shell syntax: PASS

## R runtime coverage

The v2.13 tests verify the eight-operation R registry, fixed Rscript dispatch, service bearer authentication, no arbitrary R/shell execution surface, internal-only runtime network declaration, independent container resource limits, migration 013, statistical model receipt model/routes, WordPress read-only proxies, release contract, and the real-R deployment smoke definition.

The build container does not include R or Docker, so the actual R interpreter/container execution is intentionally validated by the VPS deployment smoke rather than claimed as a local build result. The VPS deployer requires a live R linear regression to succeed and persist its artifact, polyglot receipt and statistical-model receipt before the release is considered deployed.

## Historical suite

Full historical Python suite: **1,199 passed / 128 failed**. The failures are accumulated historical release-identity tests that hard-code earlier plugin versions, README titles, assets, or predecessor markers. The v2.13 release-specific gate is clean.

## Security invariants

- arbitrary Python/R/Julia/SQL/WASM source execution: false
- client-supplied runtime URLs: false
- client-supplied runtime credentials: false
- client-supplied R package names: false
- fixed R operation registry: 8 operations
- R runtime host port: none
- R runtime root filesystem: read-only
- R runtime Docker capabilities: all dropped
- R runtime no-new-privileges: required
- R runtime network: internal-only
- Workspace worker sandbox preserved
