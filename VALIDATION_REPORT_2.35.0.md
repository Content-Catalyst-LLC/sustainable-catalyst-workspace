# Workspace v2.35.0 Validation Report

## Release
Frontend Logic Reduction & Legacy JS Retirement

## Source gates
- Backend regression: 135/135 passed.
- Current frontend boundary regression: 41/41 passed.
- Generated OpenAPI → TypeScript contract drift: PASS.
- Strict TypeScript compilation: PASS.
- Frontend reduction validator: PASS.
- JavaScript syntax: typed client, thin shell, and lazy local compatibility bundle PASS.
- WordPress PHP syntax: 31/31 files PASS.
- Python compileall: PASS.
- VPS deployer `bash -n`: PASS.

## Frontend reduction
- Historical versioned `workspace-v*.js` files: 87 → 1.
- Historical versioned `workspace-v*.css` files: 87 → 1.
- Total WordPress JavaScript files: 208 → 124.
- Primary active Workspace runtime: 6,675 lines → 24 lines.
- Browser-local project runtime retained as one lazy compatibility bundle.
- v2.28.1 delegated interaction repair retained.
- Current JS/CSS package checks derive names from `SC_WORKSPACE_VERSION`.

## Backend boundary
- New read-only `/v1/frontend-runtime` authority profile.
- Typed client endpoint count: 35.
- No new database migration. Migration lineage remains at 031.
