# Workspace v2.20.0 — Validation Report

Release target: **Workspace v2.20.0 — Monte Carlo & Uncertainty Quantification**.

Validated in the release build environment on September 17, 2026:

- Source-contract validator: PASS.
- Backend regression suite: **57 passed**.
- Targeted v2.20 + inherited v2.19/app tests: **13 passed**.
- Direct seeded Monte Carlo smoke test: PASS; deterministic 2,000-draw result produced a bounded interval and expected mean range.
- JSON release manifest, product record, and new uncertainty schemas: PASS.
- VPS deploy scripts (`bash -n`): PASS.
- WordPress PHP syntax: **31 files passed**.
- Arbitrary code execution remains disabled; the UQ runtime is defined as an internal-only, read-only, bounded-resource service.

The VPS deployer additionally verifies migration 020, runtime health, a durable seeded Monte Carlo job, top-level job-result readback, uncertainty-analysis receipt discovery, and sandbox/network controls on the live server.
