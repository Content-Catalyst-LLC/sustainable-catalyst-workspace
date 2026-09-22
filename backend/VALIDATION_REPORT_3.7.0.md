# Workspace v3.7.0 Validation Report

Release: **Claims, Evidence & Investigative Research Workspace**

## Baseline and lineage gates

- Requires the verified Workspace v3.6.0 visual-research baseline before patching.
- Requires migration `037_platform_core_visual_analysis_research_object_workspace.sql` and `backend/app/visual_research_workspace.py`.
- Requires the preserved Workspace v3.5 Analytics R provider and migration `036_catalyst_analytics_r_runtime_adapter.sql`.
- Adds migration `038_claims_evidence_investigative_research_workspace.sql`; prior migrations are retained.
- Rollback baseline is v3.6.0.

## Local release validation

- Overlay structural validator: PASS.
- Python compilation: PASS.
- Focused backend contract tests: **4 passed, 18 warnings**. The warnings are the existing Pydantic `schema` field-shadow warnings and do not represent test failures.
- FastAPI/OpenAPI operation validation: PASS; no missing operations.
- New v3.7 typed operations: **12**.
- Synthetic v3.6 fixture typed endpoints: 70 -> 82 after the v3.7 overlay.
- Production v3.6 is independently verified at 75 typed endpoints; the Mac installer requires at least 75 before patching and exactly +12 afterward. The VPS production gate therefore requires **87 or more** typed endpoints.
- TypeScript generated-contract freshness check: PASS.
- PHP syntax validation: PASS.
- JavaScript syntax validation: PASS.
- Backend-only overlay application and focused tests: PASS.
- macOS push installer shell syntax: PASS.
- VPS deployment script shell syntax: PASS.

## Production deployment gates

The VPS deployment must verify all of the following before v3.7 is accepted:

- Workspace health reports version `3.7.0`.
- Workspace v3.5 Catalyst Analytics R provider 2.1.0 remains installed and operational.
- Workspace v3.6 visual-research capabilities remain active.
- v3.7 investigative-research capabilities are active.
- OpenAPI contains every typed operation and at least 87 total typed endpoints.
- R runtime remains read-only and non-root (`ReadonlyRootfs=true User=10001`).
- Migration-037 visual snapshot registry remains present.
- All migration-038 investigative tables are present in `sc_workspace`.

The VPS script builds v3.7 images while v3.6 remains live, switches containers only after a successful build, and attempts a v3.6 runtime restore if a post-switch gate fails.

## Epistemic boundary gates

The v3.7 investigative runtime explicitly requires:

- `referenceFirst = true`
- `automaticTruthDetermination = false`
- `automaticEvidenceRanking = false`
- `automaticClaimScoring = false`
- explicit human-declared evidence relationships
- immutable evidence links and statement relations
- source-fingerprint pinning for external/non-Workspace references
- specialist object authority preserved
- no automatic decision authority
