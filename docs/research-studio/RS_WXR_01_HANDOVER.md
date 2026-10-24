# RS-WXR-01 engineering handover

Scope: RS-WXR-00, RS-WXR-01, RS-MIG-01 and the authorized RS-WXR-04.1/04.2 extensions. Overall **PARTIAL** against the complete requested platform feature set. The narrow isolated reporting and Wexford manuscript workflow is functional; production operational status, real-account browser acceptance, PostgreSQL certification and advanced scene adapters are not inferred.

## Implementation state

Completed: seven-repository targeted source SCAN; source-referenced compatibility matrix; Workspace-native private reporting route/editor; same signed-cookie/project/artifact/revision authority; read-only Lab figure/scene references; immutable saved visual snapshots; restricted LaTeX, equations, scientific tables, Workbench exact-field bindings and parameter inspection; original Lab heat-map renderer reuse with scientific units, palettes and log scales; SVG/PNG/PDF export; source/hash/access checks; isolated restart and paired SQLite/object restoration; two verified-code Wexford heat maps and a revised EMP075-derived manuscript.

Existing functionality reused: Workspace session_auth/ERW identity bridge, wxr_private_projects, repository/object_store and native models/schemas; Lab figure preview/ECDF adapter, v0.44 SVG engine and v0.153 scene contracts; Workbench v510 math-object contract; EMP071/EMP073 original research calculations. No new authentication, independent project DB, GPU engine or implicit computation from equations.

Not implemented: authenticated remote module federation/run attestation; native polygon heat maps/raw raster acquisition; correlation computation; time-dependent heat-map player; native 3D volume/5D overlays; complete drag composition/table-grid editor; tagged accessible PDF; production container packaging of optional renderers; source-rights clearance or empirical field calibration. The actual EMP075 ZIP is privately acquired and verified locally, not imported as a whole into Workspace or GitHub. Only derived heat-map JSON was staged in disposable local projects.

## Repository state

Implementation repository: `Content-Catalyst-LLC/sustainable-catalyst-workspace`; new review branch `codex/rs-mig-01-reporting-studio`, based exactly on PR #6 head `de45f37c3b1984692602ccef2f80b87a8e549094` (`codex/wxr-09-3-complete`). PRs #3/#4/#6 remain open and unmerged; no silent merge/cherry-pick. PR #6 is an explicit release prerequisite rather than production readiness evidence.

The exact scanned Lab/Workbench/Site/Core/documentation/data commits are tabulated in RS_WXR_00_SCAN_REPORT.md. No other module source was edited. Central documentation and private data registers are reconciled on separate review branches; final publication identities/URLs are appended below and supplied in the output publication manifest. Scientific deliverables stay local/private.

Changed code: backend/app/research_reporting.py, reporting_composition.py, reporting_heatmaps.py, research_reporting_ui.html/js; additive router mounting in main.py and navigation link in wxr_private_projects.py; optional reporting_math runtime/lock/vendor provenance/license; requirements-reporting.txt; isolated harness and source-reproduction scripts; versioned schema; synthetic tests; isolated CI workflow. Engineering reports/evidence are under docs/research-studio. No scientific datasets, manuscripts, raw GIS, cookies or signing secrets are included in source commits. Final changed-file list is attached to the publication manifest. Task-local work includes private scientific reproduction directories, SQLite/blob proof, QA renders and output deliverables; these are deliberately not source commits.

## Verification

Workspace selected regression: **168 passed, 4 PostgreSQL-only skipped**; 30 focused reporting tests included, do not double-count. Existing selected Lab scene/composer tests: **22 passed**. Exact commands and warnings are recorded in TESTING.md. The strengthened rollback test flushes pending SQL writes before injecting commit failure and confirms no durable project revision is added. Optional dependency audit: zero known npm vulnerabilities on the locked runtime. New exact-head CI workflow awaits its own result; local success is not CI or deployment certification.

EMP075 ZIP SHA256 `708949c511eef5b70023048a9601ce43a0858295e7eb08c919ed9c4f722f4e08`; 18/18 manifest files and byte sizes matched, duplicate ZIP identical. Original DOCX SHA256 `1718d45de0ef103e762925fd000ab942553b162b02dfc3f86dff4ac08a319b27`, PDF `6c9357c84e1991575ec97bbe3abe7cdb9c00cdf494a89daecdb14b9a007e5d24`; unchanged. All 13 EMP03G4 input-manifest files matched. EMP071 intentionally excludes an internal-map member; original code was separately pinned by SHA256. Three statistical CSVs and three spatial summary/design tables reproduced at 1e-12 tolerance. All 36 new noncentral-t grid cells passed n/n-1 checks; assumed SD/effect inputs are not measured Wexford parameters. Rainfall grid preserves 2,363 source values; no interpolation or invented missing dimensions.

Real local process stop/restart on a separate restored SQLite/object directory reopened both saved heat maps. Source hashes, SVG snapshots and deterministic PDF bytes matched exactly; six content-addressed objects verified. Browser verified signed-cookie access, reopening, PNG export and a color-scale edit saved as revision 4 with revisions 2/3 retained. This uses the harness's synthetic owner. The upstream existing-account login regression is mocked; live existing-user acceptance remains OPEN. Docker/PostgreSQL verification could not run locally because socket access was denied. No production tests or state changes occurred.

Manuscript: the EMP075 copy contains both new figures, methods, interpretation, limits and sources; all original paragraph text is retained. The inherited Figure 2 subtitle overlap was repaired using the unchanged EMP06 comparison CSV, captions were kept with source figures and table row splitting was disabled. Original manuscript and research archives remain untouched. Final page count/render review and output SHA256 are recorded in the local artifact manifest. Author interpretation, source rights, full bibliography/academic-integrity review and submission permission remain independent gates.

## Deployment and recovery assessment

Feature defaults disabled (`SC_WORKSPACE_REPORTING_STUDIO_ENABLED`). Existing signed-cookie secret/issuer/audience, native project tables and artifact store are prerequisites. Same-origin write protection remains strict; no Caddy changes included. Optional Node 26 runtime with `npm ci --prefix backend/reporting_math --ignore-scripts` and optional `requirements-reporting.txt` must be packaged and verified in an isolated image. Default backend Dockerfile remains unchanged and does not provide these optional dependencies.

No database DDL or source-record migration. Report JSON is additive and legacy scene bytes remain unmodified. Preserve a consistent database/object pair; backup-only database is insufficient. Disable the feature flag or revert the additive router/editor to roll back behavior, retaining historical JSON and blobs. Audit old-client save behavior before permitting it to edit projects containing new report objects. Never remove report data to make rollback appear compatible.

Explicit owner approval remains required for merges, production proxy/image/deployment changes, migrations if later introduced, real production import, restricted dataset redistribution and academic submission. This build does not request or perform those actions.

## Continuation

1. **RS-WXR-02:** package the optional runtimes in a disposable image, run exact-head CI and PostgreSQL concurrency/paired-restore tests, then validate a genuine existing-account project through the retained login. Add trusted module execution identity and source permissions without duplicating module engines. Acceptance: original source hashes and numeric parity, project denial, immutable report lineage, real restart/restore on the reviewed image.
2. **RS-WXR-03:** mount the preserved Lab native 3D/4D scene runtime; add Q only with declared units/domain/semantics and scientifically valid x/y/z/t/q data. Unsupported dimensions stay disabled.
3. **RS-WXR-04:** extend native composition UX, accessible tagged PDF, polygon/raster adapters, scientific category legends, frame selection and export reproducibility across runtimes. Existing raw scene, Workbench and Site contracts remain authorities.
4. **RS-WXR-05:** author review of both heat-map findings/citations and revised manuscript; retain EMP075 fallback and resolve source-rights/boundary caveats. No field-calibrated removal claim or public GIS release.
5. **RS-WXR-06:** independent real-user/browser, authorization, source-to-render, rights, GPU fallback, backup/rollback and exact-image audit. Separate owner deployment approval only after gates close.

## Publication identities

Review publication is completed after the implementation tree is checked. Exact implementation commit, review PRs and documentation/data commits are recorded by the final publication update; no completion is claimed from an unpublished local change.
