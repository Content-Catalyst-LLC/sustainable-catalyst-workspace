# G1 implementation, identity and API boundary

## Source and data flow

`backend/app/main.py` mounts `backend/app/wxr_private_projects.py` and `backend/app/research_reporting.py`. The browser editor is `backend/app/research_reporting_ui.html` plus `research_reporting_ui.js`; the latter opens the persistent-project API. Scientific bytes remain in `backend/app/object_store.py` under the configured object root. Reports are additive `research-report-reference` objects in existing project revisions, saved through `backend/app/repository.py` and `backend/app/models.py`; no G1 report table or source migration was added. Renderers are `backend/app/reporting_composition.py`, `reporting_heatmaps.py`, `lab_figure_reporting_v3842.py`, and `backend/reporting_math/`. Unsupported source schemas fail closed. Saved `rendered_view` snapshots reopen without silent rerendering.

## Two private-research project APIs

| API | Source | Authority and use |
| --- | --- | --- |
| `/v1/private-research/projects` | `backend/app/private_research.py` (`/v1/private-research` router, `/projects` routes) | Earlier private-research registry backed by `workspace_private_research_projects` and its own storage paths. Requires an existing Workspace project and signed session. It is **not** the G1 project picker or persistence authority. Existing records must be preserved. |
| `/v1/private-research/persistent-projects` | `backend/app/wxr_private_projects.py` | WXR-09.3 native project creation, reopen, file upload/download on `workspace_project_heads`/revisions and artifact heads/revisions. G1 editor uses this API. |
| `/v1/private-research/reporting-studio` | `backend/app/research_reporting.py` | Opt-in private editor, preview, save, revision reopen, PDF export. Requires the same signed subject and owned persistent project. |

See `docs/WXR_09_3_RELEASE_CANDIDATE.md` for the historical API split. A legacy `/projects` response must not be interpreted as an owned persistent project.

## Security and consistency contract

- `backend/app/session_auth.py` signs the HttpOnly Workspace cookie with HMAC-SHA256, validates signature, schema, issuer, audience and expiry; `backend/app/erw_identity_bridge.py` retains the existing account login. G1 does not register accounts. The signing secret is an external configuration value, never part of this repository.
- `wxr_private_projects._subject` derives the owner from the signed cookie; `repository.get_project` and `object_store.get_artifact` scope reads by that owner. `research_reporting._source` additionally requires the source artifact to belong to the same project and to be a private-research artifact. Other owners/projects receive 404.
- `wxr_private_projects._write` requires the **exact** `https://workspace.sustainablecatalyst.com` Origin on every unsafe G1 write. A matching CORS configuration alone is insufficient. Reverse proxies must preserve the Origin and same-origin `/v1` routing.
- Uploads calculate SHA-256, reject same-project duplicate hash/filename, and store content-addressed bytes. Reads recheck length and SHA-256 in `object_store.read_artifact_content`; G1 references pin artifact ID, SHA-256 and source revision. A hash proves byte identity, **not** scientific validity or rights.
- `research_reporting.save_report` locks the owned project row and compares `expected_project_revision`; `repository.store_project` persists the next immutable revision. Stale saves return 409. Reopen rechecks the original source and saved SVG digest. PostgreSQL row-lock behavior still needs a documented concurrent-worker test on this exact candidate.
- `SC_WORKSPACE_REPORTING_STUDIO_ENABLED` must equal `1` to enable the route. Unset, `0`, or the candidate image's `false` default yields 503; see `research_reporting.enabled`.

Tests: `backend/tests/test_research_reporting.py`, `test_wxr_private_projects.py`, `test_g1_reporting_postgres.py`, and `test_reporting_g1_acceptance.py`. The PostgreSQL G1 file is currently a synthetic owner-isolation smoke, not full concurrent-worker certification.
