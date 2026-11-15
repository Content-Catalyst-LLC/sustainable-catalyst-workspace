# SC-EDITOR-01 — Unified Scientific Authoring Foundation

**Status:** implementation candidate; feature branch, not production accepted.  
**Primary owner:** Workspace / Reporting Studio. **Consumer:** Research editorial pipeline.  
**Dependency:** existing SC-PUB-TIPTAP-01 locally bundled Tiptap 3, SC-CITE-01, RD-01.2 immutable publication store, RH editorial contracts.

## Design decision

Extend the **existing** self-hosted Tiptap editor and the canonical Workspace publication store. Do **not** create another editor runtime, document database, identity issuer, approvals service, PDF/DOCX engine, or external content provider.

The Workspace-authenticated scientific manuscript is canonical Markdown. One saved publication revision is immutable, content-addressed by SHA-256 and scoped to an owner/project. The Tiptap editor only modifies permitted text blocks. Figure assets, LaTeX, tables, code, source citations and unsupported rich syntax retain their original source bytes unless explicitly edited in Markdown mode.

## Implemented in this candidate

1. **Lossless visual admission:** the editor checks each supported block through Tiptap's Markdown serializer before enabling rich editing. If conversion changes text or scientific syntax, the block is displayed as protected source with an explicit Markdown-edit action; no silent normalization.
2. **Authenticated authoring package:** `GET /v1/private-research/reporting-studio/publication/projects/{project_id}/documents/{document_id}/authoring-package?revision=N` returns `sc-unified-scientific-authoring/1.0`. It carries canonical Markdown, SHA-256, immutable revision and project revision, frozen citation snapshot, verified figure/source references, rights/scientific statuses, and owner-scoped export/draft links.
3. **Research draft export:** a distinct action downloads the existing Reporting Studio `research-revision` JSON projection; it is **not** an approval, upload, or publication. Figures not carried into the Research projection are flagged to the researcher.
4. **Source-compatible export:** HTML, PDF and DOCX continue through their existing authenticated, source-verified endpoints. New controls are disabled when the document is unsaved/dirty.
5. **Owner-scope and integrity tests:** tests cover owner gate, revision scoping, tamper rejection, citation/figure retention, UI buttons and lossless Markdown admission.

## Contract and semantics

- `authority: workspace-scientific-publication`: Workspace remains the only authoring persistence authority.
- `manuscript.format: markdown` and `manuscript.sha256`: bytes from the saved immutable revision, independently rehashed before package issuance.
- `source` and `figureSources`: retained source IDs and verified hashes from the saved revision, not client-generated assertions.
- `citationSnapshot`: frozen Citation Studio snapshot from the saved revision.
- `handoffStatus: private-draft-not-published`, `approval: null`: no Research publishing action or redistribution authority is implied.
- `links.researchDraft`: authenticated conversion endpoint for editorial preparation only. Research must separately resolve governed objects, require rights/provenance approval, and create its own editorial revision.

No public endpoint, cross-owner token or new user identity is introduced.

## Acceptance checklist

- [ ] `cd backend/reporting_tiptap && npm ci && npm test && npm run build` with the committed lockfile.
- [ ] `cd backend && python -m pytest -q tests/test_sc_editor_01_foundation.py tests/test_rd012_reporting_studio_recovery.py`.
- [ ] Existing SC-PUB-TIPTAP-01 browser tests pass against an isolated, authenticated synthetic Workspace owner.
- [ ] Browser: visual Markdown editing of simple headings, paragraphs, lists and quotes saves the intended revision; untouched Markdown is byte-identical.
- [ ] Browser: complex citation, mathematical, table, code and asset blocks never become destructively normalized.
- [ ] Browser: two-owner checks deny cross-owner package reads and cross-project figure access.
- [ ] Browser: stale project and document revisions return 409; export buttons remain disabled while unsaved.
- [ ] Verify HTML, DOCX, PDF, authoring JSON and Research JSON against one frozen synthetic report including a pinned figure, unresolved citation and equation.
- [ ] Inspect exported Research projection's `notCarried` contents before considering editorial acceptance.
- [ ] Production deployment **NO-GO** until image rebuild, dependency/license/SBOM review, off-host backup and rollback validation, authenticated staging acceptance, and Research editorial receiving-side acceptance.

## Deployment boundary

`backend/Dockerfile.reporting` already builds the locally bundled Tiptap code from `backend/reporting_tiptap` using a pinned lockfile. No new external CDN, production configuration or deployed assets are needed for the candidate. This branch makes additive changes to the existing editor and authenticated Workspace API. The existing release gates and the owner-controlled production deployment remain authoritative.

## Not implemented or claimed

A true reusable editor mounted in Media, Library, and Research is **not** yet deployed. Neither real-time collaboration nor full math/figure WYSIWYG editing is claimed. No automatic Research publication or real-account acceptance has been performed. The authoring envelope is the cross-application contract, not a permission to bypass Workspace/Research rights and approval controls.

## Next integration

Research should accept this contract through a Workspace-authenticated, signed/verified adapter, re-resolve all figure and citation objects to current governed identities, then create an editorial revision *only* after its own checks. Implement this separately from the editor to preserve authorization boundaries.
