# Private Workspace Reporting Studio

Development only. Enable `SC_WORKSPACE_REPORTING_STUDIO_ENABLED=1` in an **isolated** environment; the default is disabled. No production configuration or schema changes are included.

The private route is `/v1/private-research/reporting-studio`. It reuses Workspace signed cookies, strict write Origin, project ownership, immutable private artifacts and native project revision history. No registration, external retrieval, scientific evaluation or second project database is introduced. Existing private-project UI links to the studio.

## Run and verify

From `backend/`, use the existing Python environment and install optional exports only where needed:

```sh
python -m pip install -r requirements-reporting.txt
npm ci --prefix reporting_math --ignore-scripts
PYTHONPATH=. python scripts/reporting_isolated.py --state-dir /tmp/sc-reporting-unique-proof
```

The dedicated harness binds only `127.0.0.1:8079`, creates a new marked SQLite directory and a synthetic owner, and exposes `/isolated-session` solely in that test app. It never mounts that bootstrap or its localhost-Origin mapping in `app.main`. Its cookie verification is the existing Workspace implementation. This is not real-account acceptance or PostgreSQL certification. Its marker prevents accidental use of an existing unrelated directory. Do not point it at production data. Optional `--seed-export` stages an inspected scientific JSON export in the disposable project. Existing authenticated projects can instead stage native private JSON artifacts through their established file UI.

Node is required only for new equation typesetting/heatmap rendering. `reporting_math/package-lock.json` pins MathJax, jsdom and transitive dependencies; `SC_REPORTING_NODE_BIN` may select the trusted Node executable. The existing backend Dockerfile is unchanged and does **not** package these optional runtimes. Package an isolated development image before release review. PDF requirements are optional pinned dependencies; absent runtime returns 503. Saved SVG snapshots reopen without retypesetting. A PDF export rechecks owner, artifact hashes and bound values before conversion.

```sh
PYTHONPATH=. python -m pytest tests/test_research_reporting.py -q
```

See TESTING.md for the full regression command, actual results and limitations.

## Supported and deferred contracts

- Lab `sc-lab-advanced-statistical-figure/0.115.0` ECDF: fingerprint checked, existing Workspace ECDF renderer reused.
- Lab `sc-lab-report-figure/1.0` and `sc-lab-report-scene/1.0`: existing preview renderer reused. Scene output is explicitly a 2D projection, never a native 3D/5D claim.
- Lab persisted `sc-lab-4d-computational-workspace-revision/0.153.0`: original bytes and provenance referenced; native runtime required for rendering/export. No migration or source mutation.
- Lab `sc-lab-scientific-visualization/1.0` regular numeric heat maps, including masked geospatial cell grids: pinned existing Lab v0.44 SVG engine reused byte-for-byte; units mandatory; coordinate/index parity, finite values and duplicate checks. Grid centers must be regularly spaced. Missing cells stay masked. Geospatial aspect ratio is preserved. Palettes and linear/positive logarithmic color scales are presentation settings; clipping, interpolation and resampling are rejected.
- Workbench `sc-workbench-math-object/1.0`: immutable artifact SHA/revision and mathObjectHash verified; exactText/decimalText/latex bindings supported. Free symbols and source precision are exposed. Execution URI is a **declaration**, not authenticated run attestation.
- Raw GIS files, arbitrary SVG/HTML, unsupported schemas, polygon regions, native volumes, correlation computation, time-series heat-map frames and 5D controls are not implemented by this adapter. Future adapters must preserve original module authority.

## Scientific composition

The editor accepts a native JSON composition: up to four LaTeX equations, a bounded table, method notes and citations. Equations support inline/display, AMS matrices and aligned derivations. Only fixed MathJax base/AMS packages run in a bounded worker; user macros, HTML, URLs, IO and dynamic extensions are rejected. Equations are typeset without evaluation. Table values are exact strings or pinned Workbench field references. Units, definitions, significant-figure metadata, uncertainty and citations are preserved. Declared precision does not fabricate additional empirical precision. Native visual table/formula layout is supported; a spreadsheet-style table editor, drag composition, semantic PDF tagging and GPU overlays remain future work.

Source exports are not automatically authenticated module outputs. All results retain source-declaration and non-field-validation disclosures. Unverified arithmetic cannot be promoted to a measured-result classification by this schema.

## Persistence and rollback

Reports are `research-report-reference` objects inside native project JSON. Save uses expected project revision, row locking, mutation receipts and immutable project revision rows. Saved SVG and metadata are snapshotted; reopening verifies underlying source and bindings and serves the historical snapshot rather than recomputing with a changed renderer. All source bytes remain in the existing content-addressed private store. Source objects are never replaced or deleted by the bridge.

There is **no DDL migration**. Preserve the paired project database and artifact store; a database alone cannot restore source references. Rollback disables the flag or reverts this additive change, preserving report JSON, revision history and blobs. Older clients may ignore the new object type; their save behavior must be audited before release. Do not down-migrate or delete unknown objects. PR #6 remains the persistence/auth prerequisite; #3/#4/#6 are not merged by this build.
