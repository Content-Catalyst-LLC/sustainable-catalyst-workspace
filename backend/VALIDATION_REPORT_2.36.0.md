# Workspace v2.36.0 Validation Report

## Release

Workspace v2.36.0 — Production Architecture Certification

## Source validation

- Backend pytest: **141 passed**; 3 inherited Pydantic field-shadowing warnings; no failures.
- Current frontend boundary regression: **46 passed**; no failures.
- Generated TypeScript/OpenAPI projection drift: PASS.
- Production architecture certification validator: PASS.
- Strict TypeScript compilation: PASS.
- Active Workspace shell JavaScript syntax: PASS.
- Local compatibility JavaScript syntax: PASS.
- Generated typed client JavaScript syntax: PASS.
- WordPress PHP syntax: **31 files** PASS.
- Backend Python compilation: PASS.
- VPS deployer shell syntax: PASS.

## Architecture certification

- PostgreSQL/Python remains canonical.
- Backend authorization remains server-resolved and default-deny.
- Browser-local canonical authority remains disabled.
- Local-first outbox remains non-authoritative.
- Scientific-object generic arbitrary mutation remains disabled.
- Cross-product handoff generic destination mutation remains disabled.
- Runtime arbitrary-code execution remains disabled.
- WordPress service credentials remain server-side.
- Thin frontend and v2.28.1 interaction repair remain preserved.
- Migration lineage remains at `031_backend_policy_identity_authorization_consolidation.sql`; v2.36 adds no migration.
- Rollback baseline is v2.35.0 and schema-compatible.
- Live public-page/cache/CDN/rollback checks remain explicit field checks; this release does not silently mark those as completed.

Final package replay and exact patch reconstruction results are recorded in `PACKAGING_REPLAY_V2360.txt`.
