# UVR-01.3.9 — Persistent Workbench figure in Workspace Reporting Studio

## Implemented receiving adapter
Workspace PR #7 already has an opt-in signed-session Reporting Studio, immutable project revision store, and a private source-artifact store. This patch allows that Studio to accept a Workbench handoff JSON `{manifest, svg}` as a **private source file** using the existing `/v1/private-research/projects/{project_id}/files` operation. The source must have schema `sc-workbench-report-figure-handoff/1.0`, hash-matched SVG bytes, nonempty graph/render/view-spec lineage, and safe static SVG content. The original source bytes remain immutable.

The **existing** `POST /v1/private-research/reporting-studio/projects/{project_id}/reports` route persists a report revision and captures the SVG snapshot. `GET /v1/private-research/reporting-studio/projects/{project_id}/revisions/{revision}/reports/{report_id}` reopens that exact snapshot, subject to existing authentication and private project/source checks. The default Reporting Studio feature flag remains disabled.

## Data flow
1. Workbench generates a source-verifiable handoff via `standalone-app/report-attachment-handoff.mjs`. Export is a source artifact, not a report write.
2. With an existing Workspace signed session, the researcher uploads the JSON handoff as a file in their Workspace private project.
3. The researcher selects that file in Reporting Studio; source artifact ID, SHA-256 and immutable artifact revision are supplied to the existing save route.
4. The report is appended through native Workspace immutable project revisions. Reopen verifies the source hash, saved visual hash, and existing execution-binding rules.

Workbench graph and Workspace project IDs **are not assumed to match**. Workspace's signed session and artifact-project ownership are authoritative for receiving storage. Workbench-origin graph identity is recorded as declared lineage; remote Workbench account attestation remains unimplemented and must not be advertised as independently verified. The report is scientifically **not certified**.

## Test and production limits
Synthetic tests exercise save/reopen and content tamper, provenance completeness, active SVG rejection. Run:
`PYTHONPATH=backend python -m pytest -q backend/tests/test_uvr_0139_workbench_reporting.py backend/tests/test_research_reporting.py`

No actual Wexford/Metrics research objects or credentials are used. Current reporting branch is review-only and may not be deployed; production is **not** certified. Requires resolving Workspace PR #7 dependencies, packaging optional reporting runtime, real-account acceptance, PostgreSQL verification, and enabling the feature through existing deployment procedure. This patch alone does not add a new user-facing 'Attach to report' control in Workbench and does not create cross-system SSO.

## Design boundary
Core remains governance authority. This is a receiving adapter, not a new rendering engine, new authentication stack, or new database. Only verified bytes/ownership **inside Workspace** are asserted.
