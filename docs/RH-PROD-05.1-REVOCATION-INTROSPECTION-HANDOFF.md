# RH-PROD-05.1 — Workspace-side revocation and introspection candidate

**Status: SOURCE CANDIDATE ONLY — NOT CONNECTED, NOT TESTED IN CI, NOT APPROVED FOR DEPLOYMENT.**

This change is additive and remains **disabled by default**. `research_session_introspection.router` has **not** been mounted in `main.py`. The existing `DELETE /v1/session` implementation now contains a feature-gated durable revocation transaction, and signed-cookie validation checks revocation on all session-authenticated paths only when `SC_WORKSPACE_SESSION_REVOCATION_ENFORCED=true`. This flag must remain off until approved migration and staging acceptance.

## Added

- `backend/migrations/051_workspace_session_revocation.sql`: durable hashed-token revocation records.
- `backend/app/session_revocation.py`: fail-closed revocation lookups/inserts and service-token validation.
- `backend/app/research_session_introspection.py`: unmounted internal POST introspection router requiring a **dedicated** Research service credential. The response is limited to verified source-subject/session claims; it **does not invent or authorize tenant scope**.
- `SC_WORKSPACE_RESEARCH_INTROSPECTION_TOKEN` setting defaults empty, making the service endpoint deny even if accidentally imported.
- Synthetic tests for revoked sessions, idempotence, unavailable database, unconfigured/invalid credentials, original-cookie replay after logout and Origin mismatch. Tests are committed but have **not** been executed in this session.

## Mandatory before any activation

1. Review and test migration on isolated PostgreSQL, confirm versioned migration-runner integration and rollback instructions. Production DB migrations must not run from an unapproved source branch.
2. **Review and execute in isolated staging** the feature-gated validation/logout integration. It checks token revocation before treating a presented cookie as authenticated, commits the logout revocation record before returning success, and fails closed on a revocation DB outage. Inspect every alternate session consumption path, concurrent logout edge, and legacy service-credential fallback.
3. Validate token issue-time, expiry, issuer, audience and unique session identifier consistently; reject legacy tokens missing the necessary claims. Assess service-token signing-key fallback for production and ensure private service credentials remain separate.
4. Expose introspection only via an authenticated, private service route with HTTPS/mTLS or equivalent approved service isolation and a strong managed secret. Add rate limits, request-body redaction and no-store response headers. Reject arbitrary Origin/CSRF-sensitive browser requests; make the endpoint unavailable on public proxy routing.
5. Require authenticated server-side service principal and a separate owner/project authorization mapping. `subject` is **not** equivalent to Research `owner_scope`.
6. Add concurrency/replay tests, expiry cleanup policy, lost/stolen token after logout, service credential rejection, DB fault injection, unknown subject and cross-tenant isolation. Run existing Workspace regressions.
7. Perform authorized real-account staging acceptance and safe deployment attestation. No work in this branch changes production services.

## Source boundary

The existing backend authority is `backend/app/session_auth.py`; the current default cookie is `sc_workspace_session`. Existing `GET /v1/session` is a browser-status endpoint and cannot be used as a replacement for authenticated private introspection.

**HOLD:** Do not merge or deploy this PR in its current state. Do not enable Research private write routes.

## Latest source integration state

- Added `SC_WORKSPACE_SESSION_REVOCATION_ENFORCED` default false. There is no migration or deployment side effect from merely merging source, but enabling the flag before schema deployment will deny cookie access.
- Implemented gated `decode_session_token` revocation checks and gated `DELETE /v1/session` same-origin enforcement + transactional revocation before clearing a browser cookie.
- Private introspection explicitly returns 503 while global revocation enforcement is disabled; router remains unmounted regardless.
- Added `backend/tests/test_rhprod05_logout_replay.py` with mocked isolated database cases. No test run or PostgreSQL acceptance has been performed by this implementation turn.
