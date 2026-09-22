# Workspace v3.10.0 Validation Report

Release: **Workspace v3.10.0 — Entity, Actor & Relationship Resolution Workspace**

## Clean-room validation

- Full repository overlay: PASS
- Backend-only overlay: PASS
- Static release validator: PASS
- Backend-only release validator: PASS
- Python compilation: PASS
- Generated TypeScript contract parity: PASS
- Focused entity-resolution tests: **5 passed**
- Typed endpoint count: **131**
- New v3.10 typed operations: **20**
- Missing expected OpenAPI operations: **0**
- WordPress PHP syntax: PASS
- WordPress JavaScript syntax: PASS
- Version-derived WordPress shell identity: PASS (`workspace-v3.10.0.css` / `workspace-v3.10.0.js`)
- Migration lineage: `041_entity_actor_relationship_resolution_workspace.sql`
- Rollback backend baseline: `3.9.1`
- Catalyst Analytics R provider preservation target: `2.2.0`

Pydantic warnings that fields named `schema` shadow a `BaseModel` attribute remain warnings only and did not fail tests or contract generation.

## Human-control assertions

Validated release contracts require:

- `automaticEntityMerge = false`
- `automaticIdentityConfirmation = false`
- `automaticRelationshipInference = false`
- `automaticCulpabilityInference = false`
- `automaticTruthDetermination = false`
- `automaticEvidenceRanking = false`

A confirmed match candidate remains a reviewed candidate record and does not merge entities automatically. `same-as` remains an explicit human-authored relationship.

## Production acceptance gates

The VPS deployment script requires:

- `WORKSPACE_V31000_PREFLIGHT=PASS typed_endpoints=131` or greater
- `WORKSPACE_V31000_HEALTH=PASS`
- `WORKSPACE_V31000_OPENAPI=PASS typed_endpoints=131` or greater
- `CATALYST_ANALYTICS_R_V220_PROVIDER=PASS`
- `ReadonlyRootfs=true User=10001`
- `WORKSPACE_V31000_MIGRATION_041=PASS`

Production deployment remains pending until these gates are observed on the Contabo backend.
