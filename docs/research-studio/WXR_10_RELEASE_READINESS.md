# WXR-10 release readiness — 26 October 2026

**NOT READY for production.** Review candidate only. No GitHub PR merge or production deployment occurred. Existing Workspace authentication, PostgreSQL revision storage, object storage, Lab renderers and Reporting Studio are retained.

## Consolidation and changes

The implementation stack is Workspace #6 (`de45f37c`) → #7 (`1f09292c`) → #9 (`2f7e4a54`) → #10. #6 includes the older persistence candidate #4 and depends on the identity/recovery reconciliation beneath it. #7 supplies Reporting Studio; #9 supplies the optional image; #10 is the single integration/review head. All earlier commits remain ancestors; do not cherry-pick overlapping implementations as independent releases.

This continuation adds one exact configurable HTTPS origin (`SC_WORKSPACE_PUBLIC_ORIGIN`) for isolated browser testing, with the production default unchanged. It also permits a choice between the two **existing** research landing pages (`SC_WORKSPACE_PRIVATE_RESEARCH_LANDING_PATH`); arbitrary redirect destinations are rejected. Staging uses `/v1/private-research/persistent-projects/ui`. The legacy production destination remains the default. A genuine account test found that the old landing page queries legacy tables absent from a fresh staging schema. The fix selects the existing persistent-project UI; it does not silently create legacy tables or add registration.

Private documentation PR #9's tracker conflict was resolved on its review branch by retaining both dated histories. Documentation #11 remains the consolidated private evidence head; documentation #8/#9/#11 and metadata-only Data #1 are separate dependencies. No research bytes or runtime credentials belong in this public code repository.

## Evidence and limits

| Gate | Executed evidence | Boundary |
| --- | --- | --- |
| Final application-source image and regression CI | `457bdc1e`: image CI 40304106858, reporting 40304106746 and recovery 40304106842 all succeeded | These attest the tested application source; later documentation-only commits do not change its tree |
| PostgreSQL reporting/recovery regression | 197 tests passed in an isolated Contabo test runner at application source `457bdc1eb3cd145fcc180cdfb97266300f5da36d` | Synthetic fixtures. Initial harness attempt had 1 failure/44 setup errors because its separate rehearsal DB was missing; rerun after provisioning that DB passed |
| Latest landing-page/identity regression | 57 passed, 1 PostgreSQL-only skipped locally; full image selection 197 passed at `457bdc1e` | No full-image skips; pre-existing deprecation/schema warnings remain |
| Mounted storage replacement | Final-source `457bdc1e` image CI 40304106858 passed create/upload/preview/save, container replacement on named PostgreSQL/object volumes, reopen/source hash/PDF and owner denial; earlier `a3c10546` also passed on Contabo | Synthetic HTTP journey |
| Paired restore and old-image compatibility | Separate restored PostgreSQL DB and object volume passed report reopen, PDF, source-hash and owner checks. Captured v3.83.0 image read the G1 project/source through its existing repository; candidate reopened it afterward | Old image does not expose new Reporting Studio routes. 294 static files restored byte-for-byte; preserved Caddy configuration validated in isolation. The later real-account application-browser rollback/forward check below passed |
| Fresh production snapshot restore | Read-only online capture restored 155 tables, 360 files, 404 artifact heads and 404 revisions with correct sizes/hashes; off-host copy verified | Object manifests unchanged across capture; writer quiescence was **not** asserted. Fresh coordinated cutover backup still required |
| Scientific preservation | 69 original, 18 EMP-07.5 and 13 EMP-03G.4 hashes matched; 128-file restricted off-device archive recovered and verified. Author-confirmed submitted DOCX preserved separately | No manuscript edits; receipt/exact submission time unverified; no WORM claim |
| Real account browser | Owner-uploaded synthetic JSON and authenticated download hash passed. Two immutable reporting revisions saved, edited and independently reopened; equation/table/provenance retained; PNG/PDF/SVG browser downloads inspected. Quiesced staging pair restored into a distinct DB/object volume and the real session reopened revision 3 with verified source hash | Actual logout/relogin and owner-completed post-restore download passed; exported bytes match. No restricted manuscript uploaded |
| Production source/image comparison | Captured image unchanged; no live application source file absent from initial candidate; initial differences confined to main/models/object store/repository/recovery-review. Session code and bridge matched before the explicit staging-origin delta | Deployed image lacks trustworthy originating Git revision metadata; source-byte inventory is authoritative |

The private release dossier holds exact hashes, restricted storage locations and later gate updates. These counts must not be added to overlapping historical suites.

## Reproduce isolated acceptance

Use a dedicated Docker host/project, synthetic fixtures, and no production database URL or volumes. The existing CI workflow `.github/workflows/wxr10-release-candidate.yml` is the reproducible image/replacement gate. The existing reporting/recovery workflows are the regression gates. Retain the exact image archive and SHA-256 manifest rather than rebuilding mutable base tags for deployment.

For genuine existing-account staging, `deploy/wxr10/compose.staging.yml` takes an exact reviewed image, the pinned existing Workbench image, two private files containing **new staging-only session secrets**, and a private directory containing only the authorized account's copied identity row. Preserve its password hash. Never copy plaintext passwords. The internal app/verifier/database network has no production connection; only the TLS proxy also joins a separate ingress network and binds `127.0.0.1:19443`. Keep PostgreSQL and objects on the separate named volumes.

```sh
# All variables below refer to private staging inputs, never production.
export WXR10_STAGING_IMAGE='<retained candidate image tag or digest>'
export WXR10_IDENTITY_IMAGE='<captured existing Workbench image digest>'
export WXR10_IDENTITY_ENV='<absolute private identity.env>'
export WXR10_WORKSPACE_ENV='<absolute private workspace.env>'
export WXR10_ACCOUNT_DIRECTORY='<absolute private single-account directory>'
docker compose -p wxr10-staging-20261026 -f deploy/wxr10/compose.staging.yml config --quiet
docker compose -p wxr10-staging-20261026 -f deploy/wxr10/compose.staging.yml up -d
# Explicit schema initialization is permitted only for this disposable staging database.
docker compose -p wxr10-staging-20261026 -f deploy/wxr10/compose.staging.yml run --rm --no-deps app python -m app.init_db
```

Forward local `127.0.0.1:18443` to the staging host's `127.0.0.1:19443` over SSH. Open `https://localhost:18443/v1/private-research/login`. The local test certificate requires the human user to handle the browser warning. The human enters the existing password; do not record credentials or export browser cookies. Test private project creation, synthetic source upload, download/hash, Reporting Studio save/edit/reopen, supported exports, sign out/in, and container replacement with the same volumes. Keep real-account and synthetic-session evidence separate.

## Approval and rollback boundary

Do not request production deployment approval until genuine-account acceptance, current-source compatibility review and the scoped rollback evidence and fresh coordinated release-point backup pass. Preserve the current image, effective configuration, static assets, paired database/object snapshot and recovery catalog. The current production image has been retained separately from the candidate.

The existing `backend/tools/wxr_release_backup.py` requires documented writer quiescence for a certified capture; never pass its confirmation flag for an online capture. It restricts restoration to a local `sc_wxr094_restore*` database. An online observed-stable snapshot is useful tested recovery evidence, but it does not waive a coordinated cutover backup.

An eventual release must use the reviewed image/configuration override with the existing Compose project and volumes. It must not run `app.init_db` against production by default. After separately approved cutover, verify login/recovery, owner isolation, source hashes, saved-report reopen and exports. If verification fails, restore the preserved image/config/proxy/static version **while retaining additive database revisions and blobs**. Data restoration is a separate potentially destructive decision. The private dossier must supply the exact existing Compose layers and tested rollback commands before approval.

## Reusable foundation

The existing `sc-research-visual-asset/1.0`, persistent projects, immutable artifact references, versioned reports, rights/evidence labels and established Workbench/Lab interfaces are the reusable contract. Preserve the provisional private SC-RI-01 contract; defer new implementation backlog until the WXR-10 release gates close. No new identity, storage, notebook or visualization architecture is introduced.

## Retained deployable image

Application source: `457bdc1eb3cd145fcc180cdfb97266300f5da36d`. All **145** application files in the retained image matched that source byte-for-byte. Application-tree SHA-256: `90a4113b9784a39883964c971e539bb284b1f47c16a065696bdf288af3e8239a`. Contabo-built Linux/amd64 image ID: `sha256:b5c775f892a99e35ac505d1ecd09b3570141a0f8c4df4103518da86fcc701007`. The loadable compressed archive is 261,081,572 bytes, SHA-256 `b09079b3e8ad3a4ede05ac2e8902f21fb170f47530b095edf0b9c1075c93c9e3`. It is retained privately; no registry publication or production deployment occurred. CI built a separate artifact for the same source; do not substitute image digests between builds.

## Final real-account and rollback continuation

Final 26 October continuation: actual browser logout denied private access; owner relogin reopened the restored edited report. The manually downloaded post-restore export matched the original byte-for-byte. Retained v3.83.0 accepted the genuine cookie, loaded its legacy UI and read the revision-3 native project with both report objects on a second distinct clone; forward candidate reopening/source hash passed. Old-image fresh-password POST from localhost was not tested. Read-only production Compose resolution preserved all 13 services, identity settings and storage/network bindings; only the reviewed backend image/landing/origin differs. Exact deployment/rollback commands are prepared and syntax checked, but production-changing commands were not run. Fresh coordinated release-point backup remains OPEN because production writer quiescence is forbidden in this certification. **NOT READY; no merge, production change or deployment approval.**

The proposed release uses only a backend image/configuration override. Existing private-research/session proxy paths already cover the delivered UI and Reporting Studio. No static/Caddy, Workbench, worker, registration or production-schema change is proposed here. The private dossier contains exact reviewed overrides, read-only Compose validation and gated release/rollback commands. The old image preserves reports as native project data; rendering returns with forward recovery. Historical restoration and broader frontend/proxy changes remain separate review scope.

## Backup-only planning update — 26 October 2026

The final backup gate remains OPEN pending explicit execution approval. A reviewed online design uses a consistent PostgreSQL dump, derives the complete artifact-reference set from its isolated restored catalog, preserves historical blobs, verifies every retained byte, and tests recovery again from an independently verified off-host copy. This can satisfy the logical database/artifact recovery contract without pausing writers; mutable auxiliary state has separate consistency epochs. It does not claim an atomic whole-server snapshot. Ten synthetic integrity/guard checks passed; no production capture or writer pause executed. Private Documentation PR #11 holds exact hashed tools, operations, impact, abort/resume rules and the single backup-only approval request. A writer pause is an explicitly separate fallback; deployment is not authorized. **NOT READY until the actual backup/recovery gate passes.**
