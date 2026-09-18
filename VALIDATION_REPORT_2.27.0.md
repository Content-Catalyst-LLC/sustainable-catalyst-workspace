# Validation Report — Workspace v2.27.0

## Release
Reproducible Scientific Study Packages

## Release gates
- Backend regression: 94/94 passed.
- v2.27 release-contract test: 1/1 passed.
- Scientific study package targeted/backend-authority/orchestration set: 22/22 passed after final integrity fixes.
- WordPress PHP syntax: 31/31 files passed.
- JavaScript syntax: PASS.
- Python compile: PASS.
- Docker Compose structural validation: 12 services.
- VPS deployer shell syntax: PASS.
- Deployer health assertion: exactly 2.27.0.
- Migration 027 included and privilege check present.
- v2.26 notebook-orchestration smoke test uses full authenticated service identity (includes X-SC-User-ID repair).
- Deterministic ZIP manifest smoke: PASS.
- Arbitrary-code execution remains disabled.
- Packaged backend ZIP replay: 94/94 backend tests passed.
- Packaged WordPress ZIP replay: 31/31 PHP files + JS syntax passed.
- ZIP integrity: all five deliverable ZIPs passed.
- Component checksum verification: PASS.
- Tiny-patch byte replay: 32/32 files exact.

## Package closure
- Incremental changed/new files from v2.26.0: 32.
- Study manifests exclude their self-fingerprint field from fingerprint computation.
- Embedded artifact snapshots are verified against raw-byte SHA-256 and byte count.
- Study bundle cleanup endpoint is included so deployment smoke tests do not leave package artifacts behind.

## Historical root contract suite
The repository also contains a large set of frozen historical release-contract tests that intentionally assert old plugin versions and historical README text. Those are not the v2.27 release gate; the current release contract and complete backend regression suite above are the operative gates.
