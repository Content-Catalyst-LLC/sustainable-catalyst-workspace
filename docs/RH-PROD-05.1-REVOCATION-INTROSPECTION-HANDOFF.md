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

## Consolidated isolated security acceptance (2026-11-05)

**PASS — GitHub Actions run 42123812986** at commit `1a09e7e279ddc45ed874fae15950bb0e63f59cd4` successfully ran the single `.github/workflows/rh-prod-05-1-isolated-security.yml` job. It installed isolated test dependencies, compiled changed modules, executed legacy plus new authentication/regression suites, applied migration 051 to a disposable PostgreSQL 16 CI service, tested original cookie rejection following logout and acceptance of a newly issued cookie, and asserted the local-only test DB target. Job steps all succeeded.

**Still HOLD for deployment:** introspection route remains unmounted and no production credentials, service networks, revocation migration, or real-account staging were changed. Broader Workspace regression suite, verified end-to-end real-account staging, owner map, private transport, and populated recovery remain outstanding. CI success is not production security certification.

## Updated private service proof and credential isolation (2026-11-05)

This section supersedes the earlier draft bearer-credential transport instructions:

- The separately started `app.research_introspection_entry:app` accepts only
  `POST /internal/v1/workspace/session/introspect` on a dedicated private
  service network; it is **not** mounted on public `app.main`.
- The caller supplies `X-SC-Request-Nonce` (64 lowercase hex digits) and
  `X-SC-Request-Proof` (canonical-JSON HMAC-SHA256 with domain-separated
  request tag). The shared proof key is never sent as a bearer or query value.
- Workspace checks proof, signed cookie validity and durable revocation, then
  loads authorized project IDs by `(user_key,project_id)` from persisted
  `workspace_project_heads`. It signs the full response in
  `X-SC-Response-Proof` with the nonce and a separate response HMAC domain.
  Research checks this proof before trusting ownership grants.
- `backend/Dockerfile` includes the `migrations` folder for the separately
  authorized migration runner. The private ASGI lifespan refuses startup
  without enforced revocation, migration/schema verification, and an explicit
  original Workspace session signing key. A generic Workspace service token
  is **not** an acceptable private cookie-signing fallback.
- Optional `SC_WORKSPACE_DATABASE_URL_FILE` and
  `SC_WORKSPACE_SESSION_SIGNING_SECRET_FILE` settings allow a separately
  provisioned SELECT-only authority DB credential and the **existing** cookie
  signer to be supplied via protected runtime files. Do not silently rotate
  the live cookie signer.
- Identical synthetic HMAC known-vector tests in both repositories guard
  against protocol drift. Workspace's isolated security CI passes.
- The companion Research draft now has an explicit immutable source
  project binding and migration `0007_reader_isolation` for restricted
  anonymous SQL-reader policies; see its private bridge implementation doc.

**No activation was performed.** The specific deployed Workspace session
signer/role/network, real-account browser acceptance, populated backup and
rollback, and complete scientific regressions remain release blockers.
Existing Wexford and Metrics records are not imported or modified.

## SC-AUTH-01 additions (2026-11-10, staging only)

All are off by default except CSRF and no-store, which apply only to cookie-authenticated requests and `/v1`/internal responses respectively.

- **Migrations:** `051_workspace_session_revocation` is renumbered to `054_…`, because 051–053 are taken on the release line. New `055_workspace_auth_hardening` adds the single-use nonce store, operator revocation by session id, per-user cutoffs, and the revocation audit. `python -m app.migrate_security` applies both in order and `require_schema` checks both.
- **CSRF:** a cookie-authenticated `POST/PUT/PATCH/DELETE` must carry an `Origin` listed in `SC_WORKSPACE_CORS_ALLOWED_ORIGINS`. `Sec-Fetch-Site: cross-site` is refused.
- **Introspection:** each request nonce is single use. It is kept until the introspected session expires.
- **No-store:** `/v1/*` and `/internal/*` responses carry `Cache-Control: no-store, private`.
- **Operator revocation:** host-only CLI, `python -m app.session_operator {revoke-user|revoke-session|purge-expired}`. It requires an actor and a reason, and every action is audited. There is no HTTP route.
- **WordPress bridge assertions:**
  - With `SC_WORKSPACE_BRIDGE_ASSERTION_KEY_FILE` (Workspace) and `SC_WORKSPACE_BRIDGE_ASSERTION_KEY` (WordPress) set to the same bridge-only key, the plugin sends `X-SC-Bridge-Assertion` instead of the service bearer and `X-SC-User-ID`.
  - The assertion is HMAC-SHA256 over the base64url claims `v, iss, aud, sub, sid=sha256(WP session token), sat=WP sign-in time, iat, exp≤iat+60, nonce, m, p, bh=sha256(body)`.
  - Workspace verifies it before routing, consumes the nonce, and applies operator `revoke-user` cutoffs to `sat`.
  - The key must differ from every other Workspace credential.
  - `SC_WORKSPACE_BRIDGE_ASSERTION_REQUIRED=true` refuses the legacy bearer + user-id path.
- **Plugin fail-closed:** account persistence returns 503 unless the dedicated backend is enabled, or the site explicitly sets `SC_WORKSPACE_LEGACY_ACCOUNT_STORE` to `true` with no backend configured.
- **Tests:** `backend/tests/test_sc_auth01_hardening.py`, plus the updated RH-PROD-05 suites.

**Still HOLD:** no production activation. Real-account acceptance is outstanding.
