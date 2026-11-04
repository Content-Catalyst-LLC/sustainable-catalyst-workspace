# SC RVF 01 implementation audit and evidence

2026-11-04. Development only. Master issue: https://github.com/Content-Catalyst-LLC/ucd-sustainable-development-research/issues/2

## Delivered segment and acceptance status

Implemented original EPA PDF checksum validation in Research Lab's existing visualization spec API, a categorical native heatmap with reported standard errors and keyboard inspection, and consumption by Workspace's existing private Reporting Studio artifact/revision workflow. Workspace generates saved SVG, source CSV, derived PNG, vector PDF and a Word figure with an editable numeric table and embedded source JSON/SVG.

This is a working local Lab-to-Workspace segment, not completion of the requested platform-wide vertical slice. No Library source record or Core identity was created; their bindings are explicitly null. No production or staging deployment, migration, merge, real-account certification, or Wexford removal claim was performed. Human extraction review and exact seven-page private DOCX parity remain pending.

## Inventory and reuse

Remote main refs were checked on 2026-11-04; see repository-heads.json. Core, Library, Lab, Workbench and Site Intelligence main refs match the October 29 source audit. Workspace main has advanced; the active Reporting Studio implementation still lives on a feature stack. Implementation here is stacked on Workspace PR 11 at 092de6fa14986ad9be11fe6a0985c275e17da0b9, which builds on Reporting Studio PR 7. Lab starts at current main 39fdefb3ff9cc73262b7d748cb44d2599094ae5a. No attempt was made to replace production from main.

| Product | Existing source and behavior reused | Remaining integration |
| --- | --- | --- |
| Core | backend/app/services/visualization_registry.py, visual_grammar.py, cross_product_visual_runtime_integration.py: versioned visual intent, immutable provenance and bindings; renderer execution excluded | Register source/version/figure identities using actual project authorization; validate producer/consumer scopes and runtime contract compatibility |
| Library | library-backend/app/cross_product_integration.py: source/artifact exchange and access scopes; existing source and artifact stores | Persist original PDF + verified extraction + citation as owned Library records; bind returned IDs rather than manufacture IDs |
| Research Librarian AI | backend/app/platform_handoffs.py: sc-research-handoff/2.0, explicit destination contract and version checks; evidence/citation models | Discovery-to-source table ingestion, DOI/citation conflict checks and authenticated receipts |
| Research Librarian WordPress | Existing navigation/product bridge; do not put scientific computation in WordPress | Expose authoritative importer without duplicating storage or calculations |
| Lab | backend/app/visualization.py build_spec/csv_text and existing /v1/visualization/spec + /csv compute-auth dependencies; assets/js/modules/scientific-visualization-engine-v0440.js | Connect imported object to existing project/artifact vault and permissioned Library/Core references; existing frontend picker does not automatically import PDF |
| Workbench | backend/app/v1350.py graph project/session ownership; existing Figure Composer and numerical modules; SVG export recovery PR 36; Workspace receiver PR 11 | Add equivalent governed categorical scientific-table intake and authoritative figure binding; no new Workbench implementation in this change |
| Site Intelligence | backend/app/platform_core_integration.py and existing attributed spatial/briefing paths | Validate CRS, resolution, license, source date and actual authorized boundaries; no site maps or fictional coordinates in this slice |
| Workspace | backend/app/research_reporting.py, repository.py, object_store.py, reporting_composition.py: owned immutable artifacts, revisions, snapshot reopening, equation/table composition; pinned Lab renderer and SVG-to-PDF pipeline | Authoritative cross-product reference picker/refresh and full manuscript export; existing Word feature here exports one scientific figure and table, not a complete academic manuscript |
| Decision Studio | backend/app/decision_object.py: scds-decision-object/1.0 evidence/provenance/uncertainty context; existing platform adapters | Permissioned source-linked independent review and competing explanations; no automatic approval/certification |

The initial inventory used existing local source checkouts and the earlier read-only reconciliation. It was followed by current remote ref checks and fresh Lab/Workspace feature checkouts. This is a source audit, not a staging runtime reconciliation. No authorized staging endpoint/account inventory was present in this chat. Prior production observations are historical evidence only and are not claimed current.

## Scientific source verification

Source: EPA Research Report 136, Table 2.4, printed p. 19 / PDF p. 26. Original PDF obtained from the current publisher reports URL. The older climate-change URL returns 404. SHA256: 9cc7ef390d6b19bd4d1a89d3b1d9c9d8c1c81e1adf8e40b6c4267d4fb93ae27a.

Transcription checked against extracted text and a rendered PDF page. Human review is pending. The copyright page says 2014 while the EPA catalog lists 2015; both fields are retained. No DOI was invented. The PDF permits reproduction with acknowledgment on p. ii. Lab's test snapshot is that public publisher report; no private paper is in either code repository.

The selected non-peat columns are Grassland + Rough grazing (average) and Arable lands, NOT grassland alone. Units are t C/ha. Values are published model-based stock estimates, not Wexford field observations or removal rates.

| Cumulative depth cm | Grassland plus rough grazing mean ± SE | Arable mean ± SE |
| --- | --- | --- |
| 0–10 | 52.2 ± 0.6 | 29.9 ± 1.6 |
| 0–30 | 127.1 ± 1.7 | 81.3 ± 4.5 |
| 0–50 | 170.9 ± 2.7 | 117.6 ± 7.2 |
| 0–100 | 213.8 ± 4.5 | 167.5 ± 12.2 |

Depths overlap and cannot be summed. No conversion to t CO2, confidence interval, annual flux, atmospheric attribution or durable removal is performed. The importer explicitly returns NOT_QUANTIFIED for net removal. A matching PDF checksum verifies source bytes, not scientific truth or human acceptance.

## Implementation details

Lab adds publisher_soil_carbon.py and an additive publisherSource dispatch in build_spec; existing authenticated spec/CSV endpoints are reused. Unknown source/hash, changed PDF bytes, oversized local source and caller overrides fail closed. The API selects a packaged publisher snapshot by ID/hash, preserving the existing request-size limit. The pinned public PDF supports deterministic offline regression. Existing native DOM renderer displays category ticks, SE labels, keyboard/pointer tooltips, an accessible table and source/warning metadata. Ordinal category zoom/pan is disabled.

Workspace extends the existing Lab heatmap adapter with bounded categorical labels, finite nonnegative SE, explicit units/uncertainty semantics and citation/checksum declarations. Numeric heatmap behavior remains covered by existing tests. Report axes retain category labels in their definitions. The adapter never promotes user metadata to source authentication.

New CSV/PNG/DOCX routes call existing open_report first, rechecking owner, project, immutable source bytes and saved SVG integrity. DOCX embeds the exact saved SVG and source object as related custom XML, the same derived PNG as the PNG endpoint, and editable data/SE cells. ZIP entry ordering, timestamps and core dates are fixed. PDF uses the existing invariant ReportLab export. Word is a snapshot; automatic refresh inside Microsoft Word is not implemented.

## Demonstration and reproduction

The local evidence was generated through Lab's real importer, then Workspace's existing HTTP file upload, preview, save, reopen and export handlers, backed by isolated temporary SQLite/object storage and synthetic signed sessions. This exercises product code; it is not a live-account browser test or a deployed integration.

1. In Lab, run `PYTHONPATH=backend python backend/scripts/import_epa_soil_carbon.py backend/app/publisher_sources/epa-report-136.pdf figure.json`.
2. In an authorized development Lab session, the equivalent API request is POST /v1/visualization/spec with publisherSource.id = epa-136-table-2.4 and publisherSource.pdf_sha256 equal to the pinned source hash. POST /v1/visualization/csv uses the same payload.
3. Stage the resulting JSON through Workspace's existing private-project file uploader; select it in Reporting Studio. Declare unit t C/ha, classification modeled, source/rights/reproduction references, then preview and save.
4. Change presentation settings to create a new saved revision. Reopening an older revision uses its saved SVG rather than silently rerendering.
5. Export SVG/PNG/PDF/CSV/Word from the saved source-bound report. The native Lab renderer also supports keyboard inspection and SVG/PNG/CSV/JSON exports.

The evidence directory epa-heatmap contains the actual Lab spec, saved reporting snapshot, structured source, SVG, PNG, CSV, Word and PDF. Local project/report IDs are synthetic test IDs and must not be used as external resolvable object identities.

## Outstanding acceptance gates

1. Complete Library/Core source registration and governed Lab/Workbench figure persistence. Current integration fields are null, not successful placeholders.
2. Supply an authorized staging inventory and test account; reconcile deployed commits and run real login, source selection, cross-product handoff, logout/login, durable restart and cross-tenant browser checks. Test sessions are not SSO certification.
3. Obtain human source extraction approval and the exact private Ahmad_Tariq_Assignment2_FinalV2.docx fixture matching b73e1e5c2a632002986f8b73a99367dbfb8193ac76d2f45d1028497b58d30e08. No matching fixture was identified in the inspected research workspace. Do not certify visual parity without it.
4. Implement figures 1/3/4/5/6, field sampling table, controlled experiments, measured discharge/chemical flux, uncertainty/lifecycle/attribution gates, Decision Studio review and complete source-linked manuscript publication.
5. Verify native Lab UI source import wiring, real-browser PNG download and visual export parity across supported clients. DOM tests and local render QA do not establish deployed browser acceptance.

No production promotion is authorized. The changes are additive code on review branches; reverting these commits removes the new importer/adapters/export routes. No schema migration or production data rollback is needed. Existing saved historical reporting revisions remain immutable.


## Executed checks

- Workspace reporting, identity, ownership, recovery and Lab adapter regressions: **184 passed, 4 skipped**. The four skips require an isolated PostgreSQL database for persistence/row-lock/migration/race cases; no PostgreSQL result is claimed. Existing model/deprecation warnings remain (84 warnings).
- Lab publisher importer, authenticated API and preexisting visualization regressions: **19 passed** (one existing TestClient deprecation warning).
- Native Lab DOM renderer: **3 passed**, including keyboard inspection, category/SE/source preservation and ordinary numeric heatmap regression.
- The 46-test focused Workspace scientific/reporting set is included in the 184 above; it is not an additional independent count.
- Word two-page rendering visually inspected after final export; SVG/PDF figure also inspected. DOCX source JSON/SVG attachments match saved source/SVG, DOCX image equals the PNG export, and repeated Word/PDF requests produce identical bytes in this environment. This is numerical/source parity, not page-layout identity between a two-page Word document and a one-page figure PDF.
- Editor/renderer JavaScript syntax and git diff whitespace checks passed. CI workflows were added/extended; remote CI results will be recorded separately.
