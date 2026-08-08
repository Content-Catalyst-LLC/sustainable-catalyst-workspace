# Sustainable Catalyst Workspace v0.6.0 — Decision Workspace

Released: 2026-08-08

## Added
- Structured Decision Workspace inside every project.
- Multiple decision records with stable IDs and canonical Decision objects.
- Options with lifecycle state.
- Weighted decision criteria.
- Option × criterion assessments scored from -5 to +5.
- Risk register with likelihood, impact, and mitigation.
- Final selection, rationale, confidence, and decided timestamp.
- Decision Studio and Catalyst Canvas handoffs.
- Public `/wp-json/sc-workspace/v1/decision-contract` contract endpoint.
- Storage schema 7 and project schema `sc-workspace-project/5.0`.

## Migration
- v0.5.0 storage schema 6 migrates non-destructively to schema 7.
- Research, evidence, analysis, identity, project, and generic object data remain intact.

## Boundary
Workspace remains free, anonymous-capable, device-local, and account-aware. v0.6.0 does not enable server project storage or cloud sync.
