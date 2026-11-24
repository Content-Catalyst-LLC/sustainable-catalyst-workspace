# RD-01.2 Reporting Studio — source/release continuity record

**Recorded:** 2026-11-01. **Status:** Local candidate tested; **not deployed to Contabo and not merged into the Workspace application source tree.**

## Delivery sequence

- **RD-01.1.2:** user-run Contabo activation; browser confirmed signed-in project catalog GET HTTP 200 and original Metrics project found. No duplicate project.
- **RD-01.1.3:** user-run import reported 25 preserved private research files and 1 provenance manifest, 26 owner-scoped legacy attachments. Production screenshot confirmed linked files.
- **RD-01.2:** separate additive release overlay for Markdown manuscript authoring, full-document preview, hash-verified SVG imports, publication revisions and saved HTML/PDF/DOCX exports. **12/12 local Python tests passed as re-run 2026-11-01; simulated browser checked previously.** No real-account Studio editor acceptance has occurred.

## Frozen baseline and delivery boundary

- Existing Metrics project ID: `ba9e54e6-2b7b-4839-beaf-3a720ca8667b`.
- GitHub research source: `Content-Catalyst-LLC/ucd-sustainable-development-research`, `papers/metrics-2026/`, source commit reported by importer `cb9ad56372ecaf95cfc055e8e3ee703aa82cfb5b`.
- **RD-01.2 bundle:** `RD-01.2-release-updated.zip`, SHA-256 `33909c856f25fb9ec63ac5344eca672e33d1cacbafb5202172c2713749a98a10`. This is a chat-authored release package; as of this record the candidate SOURCE FILES ARE NOT COMMITTED to this Workspace repository. Preserve/archive package contents into an approved source branch before claiming repository-backed code retention.
- Build drift gate depends on exact currently deployed RD-01.1.2 overlays; do not copy code over main without reconciling `app.reporting_production_entry`, project-revision contracts and tested images.
- Intended new route after successful staging and cutover: `/v1/private-research/reporting-studio/publication`. Not active merely because this document exists.

## Operator source and next gate

- [Central progress and evidence](https://github.com/Content-Catalyst-LLC/documentation/blob/main/docs/reporting-studio/RD-01.2-PROGRESS.md)
- [Canonical RD-01.2 deployment/rollback handoff](https://github.com/Content-Catalyst-LLC/documentation/blob/main/handoffs/active/reporting-studio-rd012.md)
- [Research data integration status](https://github.com/Content-Catalyst-LLC/data/blob/main/research/metrics-sustainable-development/manifests/REPORTING_STUDIO_INTEGRATION_STATUS_2026-11-01.json)
- [UCD manuscript integration handoff](https://github.com/Content-Catalyst-LLC/ucd-sustainable-development-research/blob/main/papers/metrics-2026/WORKSPACE_PUBLICATION_HANDOFF.md)

Next: preserve and review candidate source in this repository (or authorized reporting code repository); run drift-checked Contabo candidate build, then staging, guarded cutover and real Chrome/Safari owner-browser acceptance. Until that happens the live Reporting Studio still provides the figure editor and read-only research attachments, not a proven live manuscript editor.

**Outstanding feature boundaries:** live Workbench graph generation, Site Intelligence scenes, citation automation, complex Word WYSIWYG, LaTeX typesetting, and Wexford ownership/provenance recovery. No scientific or publisher licensing clearance has been inferred.

**Audit scope:** This is a scoped status/continuity record, not a source-to-runtime attestation for every Workspace service or 21-repository audit.
