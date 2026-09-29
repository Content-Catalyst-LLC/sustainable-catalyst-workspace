# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the persistent research workspace and computational execution layer of the Sustainable Catalyst platform.

**Current release:** v3.45.0 — Deep Learning Runtime Production Certification II

## Architecture

Workspace combines persistent research state, scientific notebooks, computational runtimes, governed execution, artifact exchange, and cross-product handoffs.

- **Python backend** — projects, notebooks, datasets, models, executions, jobs, provenance, runtime orchestration, scientific objects, and platform integrations.
- **Scientific runtimes** — Python, R, Julia, machine-learning, neural/deep-learning, interchange, forecasting, probability, uncertainty, optimization, reliability, and related execution services.
- **WordPress interface** — Workspace product shell, research project interfaces, local-first workflows, and platform handoffs.
- **Frontend** — browser-side workspace behavior and interface support.
- **Platform Core** — governed research objects, provenance, evidence, visual contracts, and cross-product exchange.
- **Research Lab** — experimentation and scientific-analysis workflows that can use Workspace execution.
- **Registry / schemas** — runtime, product, scientific-object, and integration contracts.

Workspace remains the execution and persistent-work-state authority for its workloads; it does not replace Platform Core's governance role or Lab's scientific experimentation role.

## Repository layout

- `backend/` — FastAPI/backend services, migrations, workers, and computational runtimes.
- `docs/` — current architecture and operational documentation.
- `frontend/` — browser application code.
- `registry/` — runtime and capability registry material.
- `schemas/` — active schemas and contracts.
- `scripts/` — deployment, validation, migration, repair, and release tooling.
- `tests/` — active regression and release validation.
- `wordpress/` — Sustainable Catalyst Workspace WordPress plugin.

## Release history

Historical release notes, validation reports, generated manifests, terminal-command files, per-version installers, and repository-local backup snapshots are intentionally not retained on the root of `main`.

The exact repository state immediately before the September 29, 2026 cleanup is preserved on:

`archive/pre-root-cleanup-2026-09-29-workspace`

Git history continues to preserve earlier source states. Generated release artifacts should live in release bundles or ignored staging directories instead of accumulating in the source tree.
