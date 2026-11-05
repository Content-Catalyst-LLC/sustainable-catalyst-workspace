# RH-PROD-05.1 — Workspace-side revocation and introspection candidate

**Status: SOURCE CANDIDATE ONLY — NOT CONNECTED, NOT TESTED IN CI, NOT APPROVED FOR DEPLOYMENT.**

This change is additive and deliberately inactive: `research_session_introspection.router` has **not** been mounted in `main.py`, and the existing login and `DELETE /v1/session` still use their original behavior.

## Added

- `backend/migrations/051_workspace_session_revocation.sql`: durable hashed-token revocation records.
- `backend/app/session_revocation.py`: fail-closed revocation lookups/inserts and service-token validation.
- `backend/app/research_session_introspection.py`: unmounted internal POST introspection router requiring a **dedicated** Research service credential. The response is limited to verified source-subject/session claims; it **does not invent or authorize tenant scope**.
- `SC_WORKSPACE_RESEARCH_INTROSPECTION_TOKEN` setting defaults empty, making the service endpoint deny even if accidentally imported.
- Synthetic tests for revoked sessions, idempotence, unavailable database and unconfigured/invalid credentials.

## Mandatory before any activation

1. Review and test migration on isolated PostgreSQL, confirm versioned migration-runner integration and rollback instructions. Production DB migrations must not run from an unapproved source branch.
2. Integrate the revocation check into **all** Workspace session decoding and authorization paths, and ensure a valid logout token is durably revoked BEFORE reporting successful logout. If the database is unavailable, fail closed; do not report a successful revocation.
3. Validate token issue-time, expiry, issuer, audience and unique session identifier consistently; reject legacy tokens missing the necessary claims. Assess service-token signing-key fallback for production and ensure private service credentials remain separate.
4. Expose introspection only via an authenticated, private service route with HTTPS/mTLS or equivalent approved service isolation and a strong managed secret. Add rate limits, request-body redaction and no-store response headers. Reject arbitrary Origin/CSRF-sensitive browser requests; make the endpoint unavailable on public proxy routing.
5. Require authenticated server-side service principal and a separate owner/project authorization mapping. `subject` is **not** equivalent to Research `owner_scope`.
6. Add concurrency/replay tests, expiry cleanup policy, lost/stolen token after logout, service credential rejection, DB fault injection, unknown subject and cross-tenant isolation. Run existing Workspace regressions.
7. Perform authorized real-account staging acceptance and safe deployment attestation. No work in this branch changes production services.

## Source boundary

The existing backend authority is `backend/app/session_auth.py`; the current default cookie is `sc_workspace_session`. Existing `GET /v1/session` is a browser-status endpoint and cannot be used as a replacement for authenticated private introspection.

**HOLD:** Do not merge or deploy this PR in its current state. Do not enable Research private write routes.
