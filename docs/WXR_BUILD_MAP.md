# Wexford Research (WXR) — Build Map and Continuity Handoff

**Updated:** 2026-10-22 (complete-project delivery roadmap)  
**Scope:** Sustainable Catalyst Workspace / Workbench private Wexford enhanced rock weathering (ERW) worked example and reusable research notebooks.  
**Status rule:** Distinguish *built*, *unit-tested*, *Contabo-tested*, *deployed*, and *authenticated production-accepted*. A standalone PASS does not imply live integration.

## Goal and architecture

Preserve the existing original Wexford ERW project (research key `SC-ERW-IRELAND-001`) and its confidential evidence, figures, calculations and manuscript. Expose the same project within authenticated Workspace without creating an empty replacement. Enable reusable reproducible notebook generation for **all** research projects via a shared Workspace service, with Workbench computation, Research Lab methods, Knowledge Library provenance, Site Intelligence observations, and Decision Studio scenarios connected through trusted project-scoped adapters.

The notebook capabilities must distinguish: generated notebook; bound/validated inputs; isolated execution; computationally replayed results; **scientific validity not assessed** until a separate scientific audit.

## Release tracker (evidence through 2026-10-22)

| Release | Scope | Verified state | Remaining gate |
| --- | --- | --- | --- |
| WXR-08.1.x | Private Workspace area and existing-login bridge | Previous private research migrations/routes installed; anonymous `401` observed | Authenticated owner mapping/browser certification |
| WXR-08.2.0 | Preservation and scientific reconciliation | Existing Workbench/Workspace database, volume and research preservation checkpoints previously confirmed | Full manuscript/evidence/figure reconciliation |
| WXR-08.3.0 | Existing Wexford project adapter | Adapter source/tests and Workspace backend deployment reported; anonymous private routes protected | **Canonical Workbench project ID + exact owner mapping, authenticated access, original editor continuity, and browser acceptance not certified** |
| WXR-08.4.0 | Notebook foundation | **11/11** tests on Mac and Contabo | Live project authority |
| WXR-08.4.1 | Evidence, equation, research-object binding | **29/29** tests on Mac and Contabo | Trusted live source adapters |
| WXR-08.4.2 | Isolated notebook execution prototype | **39/39** tests on Mac and Contabo; explicit synthetic Docker execution **PASS** on Contabo | Stronger untrusted-code sandbox and production permissions |
| WXR-08.4.3 | Independent computational replay | **56/56** tests on Mac and Contabo; two Docker replays and certificate integrity **PASS** | Real empirical inputs; scientific validity not assessed |
| WXR-08.4.4 | Versioned export research packages | **67/67** tests; Contabo two-replay package/export/version comparison/offline verification **PASS** | Authenticated live export |
| **WXR-08.4.5** | **Universal Research Notebook Service** | **78/78** tests on Mac and Contabo; synthetic replay included; universal service tests **PASS** | **Not deployed. Authorization remains callback contract only; execution is disabled in universal service.** |

The `WXR-08.4.x` **standalone foundation series is complete and a stopping point**. Do not schedule more standalone notebook foundations in place of production integration.

## Observed WXR-08.4.5 acceptance markers

The latest attached acceptance output reports:
```text
Ran 78 tests
OK
WXR0843_COMPUTATIONAL_REPLAY=PASS
WXR0844_TWO_INDEPENDENT_DOCKER_REPLAYS=PASS
WXR0844_PACKAGE_EXPORT=PASS
WXR0844_VERSION_COMPARISON=PASS
WXR0844_OFFLINE_INTEGRITY_VERIFICATION=PASS
WXR0845_UNIVERSAL_SERVICE_TESTS=PASS
WXR0845_PROJECT_AUTHORIZATION=CALLBACK_CONTRACT_ONLY
WXR0845_EXECUTION=DISABLED_IN_UNIVERSAL_SERVICE
WXR0845_PRODUCTION_DEPLOYMENT=NOT_PERFORMED
WXR0845_FOUNDATION_ACCEPTANCE=PASS
WXR0845_CONSOLIDATED_ACCEPTANCE=COMPLETE
```
Synthetic Wexford demonstration data are **not actual observed removals** and must not be presented as empirical findings.

## Critical path — next work, ordered

1. **Close WXR-08.3.0 ownership/identity mapping:** inspect the authoritative existing Workbench research-project records (do not assume column names), identify the canonical ERW project and original owner, match against authenticated Workspace identity, and prove owner-scoped access; fail closed on ambiguous/missing matches. Do not create duplicate projects or move credentials into source control.
2. **WXR-08.5.0 — Trusted Project Adapter and Live Notebook Binding:** connect Workspace authenticated project identity to the universal notebook service, authoritative model/equation/evidence objects, and revision identities. Compare object hashes and ensure existing private sources stay private. Read-only integration first. Do not trust client-supplied `owner_verified` flags.
3. **WXR-08.5.1 — Workspace Notebook Interface:** owner-scoped generate/list/verify/download actions in the existing private research UI. Verify authenticated and cross-owner denials at the API and in-browser; preserve existing Workbench editor continuity.
4. **WXR-08.5.2 — Safe Execution Integration:** opt-in task queue, hardened isolated workers, resource caps, no network by default, never mount production credentials or mutable data volumes. Separate trusted-model execution from arbitrary user code; fail closed if runtime unavailable.
5. **WXR-08.5.3 — Evidence and Manuscript Reconciliation:** populate live Wexford equations/datasets/PDF *references* (not restricted PDF bytes), figure provenance, statistical uncertainty and report artifacts; preserve scientific meaning and attribution. Keep unverified claims flagged.
6. **WXR-08.5.4 — Production Acceptance & Rollback:** single scripted test run for unit/integration, identity, cross-project isolation, data immutability, public/anonymous 401, browser workflow, package download, replay and rollback. Back up state first and capture real pass/fail evidence.

These WXR-08.5.x identifiers are **planning proposals**, not deployed releases.

## Existing deployment context (verify before operating)

- VPS: Contabo Ubuntu, Docker.
- Workspace backend source seen under `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.83.0`, backend previously on `127.0.0.1:8094`; private UI: `/v1/private-research/ui`.
- Workbench runs as `sc-workbench`, report `/erw/report`, previously on `127.0.0.1:8088`; persistent `/opt/sustainable-catalyst/workbench/data`.
- PostgreSQL Workspace container `sc-postgres`; private research tables exist but prior checks found no registered project rows.
- Previously verified preservation checkpoints include Workbench persistent directory archive, Workspace PostgreSQL dump and Workspace volume. Revalidate paths and hashes before any writes.
- Do not treat an HTTP 401 anonymous response as proof that a logged-in user is linked successfully. No production notebooks are live just because the standalone tests passed.

## Reproducible notebook release contract

A complete private project notebook should contain: immutable project/revision identification; cited evidence metadata and provenance; equations/units/assumptions; executable supported calculations; observed vs modeled vs synthetic classifications; random seeds and environment details; generated original figures; numeric results and tolerance policies; independent replay records; and an integrity-checked, versioned export with `.ipynb`, manifest, lineage and checksums.

Production publication requires (a) authenticated ownership, (b) trusted authoritative source bindings, (c) explicit approved execution, (d) correct preservation of licenses and confidential sources, and (e) clear labels separating computational reproducibility from scientific validation.

## Operator continuity requirements

- Favor **one combined acceptance command** over sequences of small diagnostics.
- Stop on failure and retain diagnostic outputs; distinguish blocked, tested, deployed and certified.
- Do not alter original Wexford research or private PDFs when testing integration.
- No secrets, tokens, user records, confidential literature files or personal credentials in Git or public export bundles.
- No fabricated PASS markers, modeled observations, carbon-credit claims or unsupported CDR effectiveness claims.
- Maintain versioned release source, test totals, deploy markers, backups, rollback, and precise links to the relevant commit in future updates.


## Full project definition of done

**This project is not complete at WXR-08.5.4.** That release would certify the initial notebook integration, not the entire Wexford research/reporting effort. Declare the project finished only after ALL of these demonstrably pass:

1. **Original-project continuity:** the *same* pre-existing Wexford ERW project appears and opens in the authenticated private Workspace; Workbench data, source PDFs, calculations, original figures, history and editor access remain intact. No duplicate/replacement or unnecessary registration.
2. **Scientific completeness:** actual research question, source inventory, assumptions, soil/basalt scenarios, constraints, units, stoichiometry, additionality/baseline, sensitivity/Monte Carlo, measurement/MRV limits, carbon-removal durability, uncertainty and Ireland/Wexford applicability are reconciled and reviewed. Derived estimates are not represented as field observations.
3. **Reference and claim audit:** every material claim, data series, equation, figure and table has a resolvable provenance link, document/version hash and review disposition; missing/contradictory evidence blocks scientific sign-off.
4. **Workspace capability:** a permitted user can use the integrated Workspace/Workbench/Lab/Library/Site Intelligence functionality to investigate, update, save, version, rerun and export the project without terminal intervention.
5. **Notebook reproduction:** genuine project-bound notebook and environment manifest can be downloaded; isolated execution, independent replay, tolerance checks and certificate state are truthful; no secrets/private PDF bytes in public packages.
6. **Manuscript and publication assets:** editable report (DOCX or suitable editable format), print-ready PDF, tables, citations/bibliography, source-attributed original figures and permitted visual addendum are delivered, with reviewed page, citation and figure conventions. Document exports must be individually inspected. Deliverables must reflect the *actual* current research and any assignment/publication specifications verified at final review.
7. **Secure production acceptance:** authenticated owner, anonymous, unauthorized and cross-project checks; backup/restore; rollback drill; trusted execution isolation; replay/export; service health and browser end-to-end tests PASS with captured evidence.
8. **Reusable platform template:** start a second *synthetic* non-Wexford research project and demonstrate the same notebook, evidence binding and report pipeline without Wexford-specific hardcoding.
9. **GitHub and operator continuity:** code, migrations, scripts, non-sensitive fixtures, scientific method documentation, release notes, test evidence indexes, architecture and final build map committed; deployed commit SHAs/tags recorded; no confidential papers, user records or credentials committed.
10. **Final owner acceptance:** user reviews the Wexford scientific report and integrated Workspace experience; unresolved exceptions explicitly documented and no false completion labels.

## End-to-end roadmap through final completion

This extends the existing committed 08.5.x notebook-integration plan. **08.6.x–08.12.x are proposed release identifiers and acceptance scopes, not verified builds or guaranteed build counts.** Consolidate releases only where gates and rollback stay independent.

| Phase / build | Deliverable and acceptance evidence | Prerequisite | Status |
| --- | --- | --- | --- |
| **G0: WXR-08.3.1** | Owner/project identity reconciliation; canonical Workbench project ID, Workspace identity and no-duplicate listing; authenticated browser PASS; preserve source, session and prior backups | Existing 08.3.0 | **BLOCKED / next critical gate** |
| WXR-08.5.0 | Trusted authority adapter for real project revisions, evidence, equations and notebook service; server-side identity enforcement, read-only first | G0 | Planned / no live acceptance |
| WXR-08.5.1 | Notebook Workspace UI: generate, inspect, list, verify, download, versions, user-visible certification limits | 08.5.0 | Planned |
| WXR-08.5.2 | Hardened execution queue, least-privilege worker, network and data restrictions, quotas, timeout, independent replay | 08.5.1 | Planned |
| WXR-08.5.3 | Bind real Wexford evidence/manuscript revisions and import provenance to notebook context | 08.5.0 | Planned |
| **G1: WXR-08.5.4** | Notebook service production audit, identity and cross-project security, backup/rollback and browser acceptance | 08.5.0–.3 | Planned **intermediate gate** |
| WXR-08.6.0 | Authoritative Wexford project manifest, all private literature source references, dataset inventories, duplicate/missing-content audit, content hashes and explicit licensing/access classes | G0/G1 | Planned |
| WXR-08.6.1 | Claim-to-source and figure/table/equation lineage reconciliation, independent citation validation and review log | 08.6.0 | Planned |
| **G2: WXR-08.6.2** | Evidence freeze: versioned reviewed data/claims, unexplained gaps documented, no false attribution | 08.6.1 | Planned |
| WXR-08.7.0 | ERW geochemical model review: basalt/mineral composition, stoichiometric theoretical maximum, mass balances, alkalinity/carbonate accounting, units | G2 | Planned |
| WXR-08.7.1 | Wexford agricultural baseline and scenario reconciliation: soils, application rate, transport/input emissions, additionality and boundary assumptions | 08.7.0 | Planned |
| WXR-08.7.2 | Uncertainty and sensitivity audit: ranges, correlations, Monte Carlo seeds/convergence, parameter provenance and calibration limits | 08.7.1 | Planned |
| **G3: WXR-08.7.3** | Scientific calculation independent replay and specialist/manual review; theoretical potential clearly separated from measured durable net removal | 08.7.0–.2 | Planned |
| WXR-08.8.0 | Wexford geospatial/time data bindings and observation timestamps; authoritative provenance, boundary and resolution controls | G2 | Planned |
| WXR-08.8.1 | Original figures, maps, diagnostics, uncertainty plots and 4D visual scene exports; static accessible outputs and image integrity | 08.8.0, G3 | Planned |
| **G4: WXR-08.8.2** | All report figures map to traceable analytic objects and declared input datasets; visual QA | 08.8.1 | Planned |
| WXR-08.9.0 | Manuscript reconciliation and section-level evidence links; limitations, additionality, MRV, permanence and policy interpretations accurately represented | G2–G4 | Planned |
| WXR-08.9.1 | Editorial export: editable DOCX, print-ready PDF, figures/addendum, footnotes or required citation style and bibliography | 08.9.0 | Planned |
| **G5: WXR-08.9.2** | Human proofread and scientific-report acceptance: pages, captions, evidence, source attributions, citation consistency, PDF and editable export QA | 08.9.1 | Planned |
| WXR-08.10.0 | End-to-end Wexford private Workspace journey: open existing project, reproduce analysis, update revision, view figures, generate notebook and report, export | G1–G5 | Planned |
| WXR-08.10.1 | Cross-module integration tests and no-hardcode generalization to a separate synthetic research project | 08.10.0 | Planned |
| **G6: WXR-08.10.2** | Research workflow completion test with real authorized owner and independent fresh browser session | 08.10.1 | Planned |
| WXR-08.11.0 | Deployment/security hardening, CI checks, GitHub reconciliation, backup/restore exercise, least privilege, logs and negative tests | G6 | Planned |
| WXR-08.11.1 | Production release/rollback drill, release manifest with image/commit hashes, user-facing acceptance package | 08.11.0 | Planned |
| **G7: WXR-08.11.2** | Full cross-service production certification after independent test environment verification; no unresolved critical defects | 08.11.1 | Planned |
| **WXR-08.12.0** | Final research deliverables, reproducibility archive, scientific caveats, runbook and operational handoff; owner review | G7 | Planned |
| **G8: WXR-08.12.1** | FINAL PROJECT ACCEPTANCE: all definition-of-done criteria checked, proof links stored, deviations waived explicitly; only then close WXR research project | 08.12.0 | Planned |

**Planning estimate:** 5 currently planned 08.5.x releases, plus 21 proposed 08.6.x–08.12.x releases, and a separate 08.3.1 identity remediation gate. These are an **initial scope estimate rather than a promised fixed build count**. Actual releases can be merged/added following audited acceptance without changing the final definition of done. No development is deemed complete based solely on unit-test totals.

## Workstreams and sequencing

- **Critical sequential path:** G0 identity → G1 notebook live → G2 evidence freeze → G3 scientific math → G4 visuals → G5 manuscript → G6 full research workflow → G7 production → G8 final approval.
- **Parallel when safe:** documentation, optional figures, literature inventory and draft manuscript review can advance while identity is pending, but cannot certify the integrated private project without verified ownership.
- **Dependencies outside the release engine:** access to the original authenticated research records, licensed reference PDFs, third-party observation provenance, actual report specifications, and human scientific judgment. Record blockers rather than synthesize substitute data.
- **Change management:** Each build must document prerequisite release SHA, source revision, migrations (if any), test commands and counts, signed-off acceptance evidence, backup, rollback and impact on original data; include `BLOCKED`/ `NOT_ASSESSED` where appropriate.

## Consolidated final acceptance matrix

| Gate | Evidence required | Blocking failure |
| --- | --- | --- |
| Ownership and session | Authenticated Wexford opens, exact original Workbench/Workspace mapping; unauthorized/cross-owner deny | Any unverified identity, duplicate project or unauthorized retrieval |
| Data preservation | Pre/post checksums, original evidence/figures/outputs and database restore rehearsal | Unintended deletion, overwrite or missing originals |
| Scientific integrity | Reviewed equations, units, baselines, assumptions, sources, uncertainty and independent recomputation | Unexplained or fabricated result, citation, dataset or figure |
| Reproducibility | Notebook with versioned environment, source metadata and at least two independent replay runs with documented tolerances | Any invented 'scientifically validated' designation |
| Reporting | Editable manuscript, final PDF, tables and figures pass human visual/editorial checks | Broken exports, unresolved citation or visual mismatch |
| Universal feature | Second synthetic project exercises same service without Wexford-specific branches | Wexford-only implementation |
| Security | Auth, tenant isolation, resource limits, negative tests, secrets scanning and auditability | Any critical vulnerability |
| Operations | Rollback, backups, deployment artifact hashes, uptime/health, release docs, GitHub commits | No recovery path or non-reproducible deployment |
| Owner sign-off | Final walkthrough and explicit completion record | Missing approval |

## Next operator instruction (single-entry handoff)

1. **Do not begin more isolated notebook builds.** The 08.4.x foundation is complete.
2. Resolve **G0 / WXR-08.3.1**, using a single non-destructive inspection and authenticated test runner to identify the genuine Workbench project row and owner. Avoid guessing schemas or generating an approval record from synthetic identity assertions.
3. Advance **WXR-08.5.0** only with a trusted actual Workspace identity contract and fail-closed evidence binding. Its development can be tested without production mutation; keep live activation disabled until G0 PASS.
4. After each phase, update **this same GitHub build map** with actual statuses, independent acceptance logs, blockers and exact commit references. Do not replace the master map with a separate ambiguous tracker.

_This roadmap is a planning/documentation artifact. It does not itself deploy code, certify scientific conclusions, or imply an already-live notebook UI._

## Production identity configuration repair — 2026-10-22

A read-only inspection found that the deployed ERW identity bridge was present in the running image, but the active Compose invocation omitted the existing `docker-compose.wxr0813.yml` override. Consequently, `WXR0813_ERW_INTERNAL_URL` was empty even though the existing Workbench identity verifier was reachable on the shared internal network. The registered ERW account store already contained one identity; no account creation was needed.

The existing override was activated for **only** `sc-workspace-backend`, pointing the bridge to `http://sc-workbench:8088`. The prior container configuration, Compose files, image ID, source digests and rollback command were saved in a restricted server-side backup before recreation. The image ID and four deployed source-file digests were verified unchanged. No source patch, image rebuild, Workbench restart, ownership transfer, grant provisioning or research staging was performed.

Verification evidence:

- 15 local tests exercise the unchanged deployed bridge using explicitly synthetic fixtures: secure native cookie issuance, verifier configuration gating, mismatched/invalid identities, Origin/header checks, forged-header rejection and durable rate limiting. These are not real-user authentication certification.
- Seven production HTTP checks pass: public homepage/session/login `200`, both private Wexford endpoints anonymous `401`, forged-identity headers still `401`, and an untrusted-Origin login attempt `403`.
- The current rate-limit directory is persistent and writable; the internal ERW verifier reports durable signing configured.
- Twelve Wexford project candidates exist under different historical owner subjects. Only one candidate matches the currently registered ERW account, and that candidate is the newer onboarding record. The canonical recovered project and historical ownership must **not** be inferred from the shared research key or from successful login alone.
- The expected private consolidated recovery directory exists. The runtime has neither an operator digest nor an operator grant-file configuration.

**G0 gates remaining immediately after the configuration repair (superseded by the authenticated acceptance below):** a real existing-account browser login, exact owner/project reconciliation and genuine cross-owner denial evidence. Operator authorization and isolated staging remain blocked; no approval flags or identities were fabricated. Keep the existing-login page as the next user action and preserve all historical project records.

### Authenticated acceptance and explicitly approved recovery review

The existing account holder completed the real ERW browser login. Native `/v1/session` reported authenticated signed-cookie access, its upstream owner digest matched the existing ERW identity record, and the protected Wexford UI opened. The general private Workspace list correctly contained zero attached projects. This closes the **real login/session check only**, not historical ownership reconciliation.

The human account holder separately approved time-limited private review of the recovery catalog, explicitly preserving all historical owners. The `wxr_recovery_review` adapter implements this narrower scope with an expiring, exact-subject, exact-catalog-digest administrative grant. It provides only GET inventory/status/UI endpoints, strips server source paths and unrelated internal fields, and grants no artifact-byte downloads, staging initialization, import, owner changes or publication. Missing/expired/mismatched grants deny access. The catalog is mounted read-only. Approval is not presented as scientific validation or an independent staging approval.

Twenty-four synthetic local tests cover granted access, other signed subjects, anonymous/forged identities, grant expiry/scope/permissions/symlinks, source-integrity changes, response privacy and UI script restrictions. Deployment and real browser acceptance passed on 2026-10-22: the signed-in account loaded the actual catalog and expanded both calculation and artifact inventories. The live view reports 20 projects, 85 calculations, 56 artifact occurrences and 50 unique artifact files. All 52 recovery checksum entries still pass. Anonymous UI/catalog/status and forged-identity requests are denied; the catalog mount is read-only and the grant file has mode 0600. The grant expires 2026-10-23 at 19:53:23 UTC (14:53 Central). The resolved production Compose override validates without shell-only variables. A prior immutable image and source/configuration backups provide rollback.

G0 historical mapping and the staging grant remain unresolved. Only one real account exists, so production cross-account isolation has not been certified; denial for a second signed subject is covered by synthetic local tests. The public repository contains generic adapter/configuration/tests only, never the private catalog, live grant or recovered artifact data.

### Controlled restoration implementation candidate — 2026-10-22

The accepted reconciliation now advances to **controlled restoration into the existing Workspace**, with deterministic dry-run validation as its preflight. The feature branch adds the private research area, exact source/target authorization, partial selective record/document restoration, native artifact handling and server-owned rollback receipts. Original owner and project identities remain immutable; unknown environment/figure associations and diagnostic projects remain restricted. Independent records do not wait for unrelated unresolved records.

This is a candidate for review, not a deployment or proof that the historical corpus is restored. See `docs/controlled-research-restoration.md` for API, source provenance, additive migration, backup verification, activation gates and rollback. The observed API version is 3.83.0; a full live-source/identity overlay reconciliation is still required before any production deployment. Restoration is disabled by default and needs separate authorization, verified backup/restore evidence and explicit human deployment approval. Existing review-only access is not a restoration grant.

## WXR-10 production-readiness continuation — 26 October 2026

Workspace #6 → #7 → #9 → #10 remains one stacked **review-only** candidate. See [current readiness record](research-studio/WXR_10_RELEASE_READINESS.md). Preserve the existing implementation and all prior commits. Final application-source `457bdc1e` isolated Contabo PostgreSQL regression: **197 passed**; latest configured-landing focused regression: **57 passed, 1 skipped**. Genuine existing-account authentication and private project creation passed; upload/report/export/logout/relogin/restart acceptance is in progress. The landing test exposed a legacy-UI schema dependency; staging now selects the existing persistent-project workspace through a bounded configuration setting. Production defaults remain unchanged. All three final-application-source CI workflows passed (40304106858/40304106746/40304106842). Current production snapshot restored in isolation: 155 tables, 360 objects and 404/404 artifact references verified. Coordinated cutover backup, completed real-account acceptance and browser rollback remain required. **Production NOT READY; no PR merges or deployment.**

26 October real-account follow-up: manual synthetic upload and authenticated byte/hash download passed; two Reporting Studio revisions independently reopened with equation/table/provenance, and PNG/PDF/SVG exports passed. The quiesced **staging-only** database/object pair restored into distinct storage and the real browser session reopened revision 3 with verified source hash. Fresh sign-in/post-restore export await owner handling the renewed local test-certificate warning. Browser rollback and coordinated cutover backup remain open. No production change or deployment approval.

Final 26 October continuation: actual browser logout denied private access; owner relogin reopened the restored edited report. The manually downloaded post-restore export matched the original byte-for-byte. Retained v3.83.0 accepted the genuine cookie, loaded its legacy UI and read the revision-3 native project with both report objects on a second distinct clone; forward candidate reopening/source hash passed. Old-image fresh-password POST from localhost was not tested. Read-only production Compose resolution preserved all 13 services, identity settings and storage/network bindings; only the reviewed backend image/landing/origin differs. Exact deployment/rollback commands are prepared and syntax checked, but production-changing commands were not run. Fresh coordinated release-point backup remains OPEN because production writer quiescence is forbidden in this certification. **NOT READY; no merge, production change or deployment approval.**

## Backup-only planning update — 26 October 2026

The final backup gate remains OPEN pending explicit execution approval. A reviewed online design uses a consistent PostgreSQL dump, derives the complete artifact-reference set from its isolated restored catalog, preserves historical blobs, verifies every retained byte, and tests recovery again from an independently verified off-host copy. This can satisfy the logical database/artifact recovery contract without pausing writers; mutable auxiliary state has separate consistency epochs. It does not claim an atomic whole-server snapshot. Ten synthetic integrity/guard checks passed; no production capture or writer pause executed. Private Documentation PR #11 holds exact hashed tools, operations, impact, abort/resume rules and the single backup-only approval request. A writer pause is an explicitly separate fallback; deployment is not authorized. **NOT READY until the actual backup/recovery gate passes.**

## WXR-10 preservation/handoff checkpoint — 26 October 2026

Online-only production backup approval was received. Attempt 01 completed its dump/catalog and local isolated restoration steps but stopped at the final order-sensitive service-fingerprint guard. Follow-up reproduced mount-list ordering changes while canonical mount contents, identity/configuration, images and start times matched; writers remain running/unpaused. Attempt remains INCOMPLETE, without a final manifest or off-host returned-copy certification. All failed evidence was preserved privately, including independently hash-checked off-host copies. Diagnose the guard and use fresh attempt names; do not overwrite/recertify failed evidence. **NOT READY; no production pause/data/config changes, merge or deployment.** The private master tracker and consolidated handoff contain precise continuation commands. Stop after this low-usage preservation checkpoint; do not repeat research or broad tests.
