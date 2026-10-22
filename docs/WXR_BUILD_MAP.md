# Wexford Research (WXR) — Build Map and Continuity Handoff

**Updated:** 2026-10-22  
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

## Immediate next handoff

**Start by closing WXR-08.3.0 authenticated original-project mapping.** Then build the trusted Workspace adapter for WXR-08.4.5's universal service. **Do not** deploy execution merely because 78 unit tests passed.

_This is a documentation-only continuity update. It does not deploy code or change VPS state._
