# RH-PUB-01A — Workspace source-authoritative project identity handoff

**Record date:** 2026-11-07  
**Status:** Research source candidate implemented and CI-validated; Workspace coordinated draft candidate extended with a >100-project test. **No real-account production certification or deployment.**  
**Research implementation:** RH-PUB-01A draft PR #26, based on coordinated PR #23, both in the private Research repository (not public).  
**Workspace upstream:** [RH-PROD-05.1 private authority PR #16](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace/pull/16).  
**Research spec:** RH-PUB-01A private identity owner gate, `docs/RH-PUB-01A-PRIVATE-IDENTITY-OWNER-GATE.md` in the private Research repository (not public).

## Handoff requirements

Workspace is the **authoritative service** for the current signed user session, durable revocation and per-project `ProjectHead` membership. It must validate the existing signed Workspace cookie using its original issuer/audience/session signer and return an HMAC-proven, nonce-bound, `research-private` response to the pre-existing **internal-only** `/internal/v1/workspace/session/introspect` endpoint.

When Research sends `project_id: "<selected-parent-project>"`, Workspace must:
1. Reject a revoked/expired/badly signed Workspace session before testing project access.
2. Query the authoritative persisted Workspace project heads for that verified user **and exact project**; do not use caller-selected identity/owner/tenant headers.
3. Return either **only the exact project ID in `authorized_projects`** (signed no-store response), or 404 for no current grant. This must work for an account with more than 100 other projects, even though unrestricted listing is capped at 100.
4. Never issue a public token, service credential, private user data, source manuscript or project membership list to an anonymous browser.
5. Remain private-network-only, with purpose-specific service secret, no public host port and no general Workspace app introspection route.

Research then verifies signed response and fresh issuer/subject/session/owner scope and writes an immutable local mapping of `ResearchProject` to the exact authorized Workspace project. It rechecks grants before sensitive operations. Workspace remains the project owner authority; Research remains the entry/workspace and future release authority.

## Candidate validation and production blockers

- Workspace draft PR #16: synthetic proof, session revocation, 2-owner and exact project-selection checks; RH-PUB-01A extends the fixture with **>100 source-owned projects, full-list denial but exact-scope success, and foreign-owner denial**.
- Research draft PR #26: private `GET /authority/projects/{id}`, scoped CSRF issuance, verified `POST /private/projects` registration, tampering/CSRF/revocation/outage denial, synthetic SQLite and PostgreSQL tenant-RLS tests.
- Remaining gates: verify **actual** deployed Workspace session signer and all custom login/logout handlers; migration 051/schema ledger and revocation enforcement; isolated private identity service and nonowner Research writer; full Workspace regression; existing-account session lifecycle and a separate owner; populated backup/restore, rollback and public-route denial. No production access or publication feature can be enabled before these pass.
- No new Workspace password system, no separate Research login, no data movement, no public WordPress write route, and no publication-approval bypass.

## Immediate next action

Coordinate workspace draft PR #16 and Research PR #26 against the exact release images in isolated Contabo staging. Do **not** claim a live owner bridge merely because the source code or GitHub workflow is green. Publication output registry and publishing controls remain RH-PUB-01B+.
