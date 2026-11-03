# RD-01.4-PB05 — Authenticated browser integration (isolated synthetic Workspace)

**Status: built and locally tested, NOT YET run on Contabo.** Date: 2026-11-03. Parent: PB04's successful disposable PostgreSQL acceptance. **This stage is NOT the real existing Workspace account or a production login.**

## What this builds

A **persistent, SSH-tunnel-only HTTPS test Workspace** on Contabo using the existing RD-01.4/PB04 publication router and installed WXR private-project router. Both use the actual Workspace signed HttpOnly cookie implementation, real PostgreSQL, and existing artifact/revision storage. No new application/database/auth system is deployed to production. The stage is intentionally in a separate Python application entrypoint and its own Docker network, test-only database, object volume and test-only signing secret.

- HTTPS browser URL: **https://localhost:18443/__pb05__/login** through SSH tunnel, not on the public domain.
- Strict exact Origin: `https://localhost:18443`. Test-only hash-checked copies change **one hardcoded `ORIGIN` line** in each source module, keeping existing strict CSRF equality checks. The original deployed sources remain unchanged and the stage rejects any different module hashes.
- Two high-entropy, separate synthetic test login codes (A and B). The stage uses native `session_auth.issue_session_token` to issue Secure, HttpOnly, SameSite=Strict test cookies; test account IDs are not real Workspace accounts. It does not accept real credentials and does not read live login records.
- Native Create Project form; PB04 editor for scientific report and policy brief; a stage-only catalog links to editors and exposes a document-metadata-only JSON acceptance receipt.
- Database and object store use separate **named volumes** that survive a stage web-container restart. No production volumes mounted, no production DB, no proxy modification, no live service restart.
- Docker web port published **only** to Contabo loopback `127.0.0.1:18443`, accessible from Mac through SSH. Docker's internal test network blocks routable access to other containers; readiness check fails closed if published localhost tunnel is unavailable.

## Mac: start the isolated browser stage

Have the previously tested PB04 ZIP in `~/Downloads` plus this package ZIP. In Mac Terminal:

```bash
cd ~/Downloads
unzip -oq RD014_PB05_Authenticated_Browser_Staging_2026-11-03.zip
bash RD014_PB05_Authenticated_Browser_Staging_2026-11-03/scripts/PB05_STAGE_FROM_MAC.sh \
  | tee ~/Downloads/PB05_STAGE_START_RESULTS.txt
```

The script copies exactly the hash-verified PB04 module plus PB05 stage source to the **new isolated** Contabo directory `~/rd014-pb05-browser-stage`, derives strict localhost Origin overlays from the previously inspected installed native private-project source, generates test-only secrets + 7-day localhost TLS cert, then starts an isolated persistent PostgreSQL database and HTTPS app. It aborts if an earlier PB05 test stage exists. Existing Workspace and Metrics are not changed.

If `postgres:16-alpine` is not cached, the script exits without starting; `docker pull postgres:16-alpine` is a **separate** operator action. If the stage HTTPS check fails, the script removes only newly created PB05 containers/network/volumes and preserves protected local logs/source for diagnosis; do not weaken the source origin/cookie protections.

## Mac: SSH tunnel and browser sign-in

1. Open a **new** Mac Terminal and keep this SSH tunnel running:

```bash
ssh -N -L 18443:127.0.0.1:18443 catalystadmin@94.72.113.77
```

2. In a **different** terminal, retrieve the **test-only** access code A from your private Contabo account (do not paste into chat or repository):

```bash
ssh catalystadmin@94.72.113.77 'cat "$HOME/rd014-pb05-browser-stage/secrets/login-code"'
```

For second-owner browser isolation, use `other-login-code` instead of `login-code`, in a separate browser/private window after signing out A.

3. Open `https://localhost:18443/__pb05__/login` in Safari/Chrome. The test cert is self-signed and may require a **local exception for localhost only**. Before proceeding, confirm the cert fingerprint shown by the start script against the local copy you retrieve from the same SSH account (`scp catalystadmin@94.72.113.77:~/rd014-pb05-browser-stage/tls/localhost.crt ~/Downloads/PB05-localhost.crt` then `shasum -a 256 ~/Downloads/PB05-localhost.crt`); **never enter your real Workspace password**. No public DNS or real-domain cookies are used.

4. Enter test code A. The catalog opens. Click **Open native Create Project interface**, create **PB05 Wexford ERW — Synthetic Browser Acceptance** once, return to `/__pb05__/catalog`, reload, and open its two-publication editor.

5. Save different synthetic text for **Assignment 1 — Scientific Report** and **Assignment 2 — Policy Brief**. Reload, switch between reports, revise only Assignment 1, and confirm Assignment 2 is unchanged. This uses the real native backend artifact revisions.

6. Open `/__pb05__/receipt` while signed in. Confirm one synthetic project and separate document revision counts/hashes. Sign out using the catalog's button, sign in again with code A, and reopen both manuscripts.

7. Restart only the PB05 **test web** container (not Postgres or live containers):

```bash
ssh catalystadmin@94.72.113.77 'docker restart sc-pb05-browser-app'
```

Reload and sign in again, then check both documents and their receipt again. The PostgreSQL and object volumes persist. Test a second private browser window using code B: its catalog must not show A's project, and directly opening A's editor link must return 404.

Do **not** upload the actual Wexford assignment documents, copyrighted publisher PDFs, live credentials or real research files to this synthetic staging stack.

## Acceptance markers and completion boundaries

**Startup markers** (produced by script only when real checks pass):

```text
PB05_DB_READY=PASS
PB05_SCHEMA_INIT=PASS
PB05_STRICT_HTTPS_STAGING_ORIGIN=PASS
PB05_STAGE_HTTPS_READY=PASS
PB05_PRIVATE_PROJECT_ROUTER=MOUNTED_IN_ISOLATED_APP_ONLY
PB05_PUBLICATION_ROUTER=MOUNTED_IN_ISOLATED_APP_ONLY
PB05_PRODUCTION_CHANGES=NONE
PB05_STAGE_RUNNING=PASS
```

**Browser acceptance** must be documented by an actual user session, screenshots or the owner-scoped `/__pb05__/receipt` before/after re-login and restart. There is no automatic `PB05_BROWSER_ACCEPTANCE=PASS` marker in this package. The local tests cover stage-login/CSRF/session/catalog and response structure but do not replace real browser acceptance. PDF/DOCX export and real-account release are still separate gates.

## Cleanup after capturing test evidence

**Do not run until test evidence has been preserved.** To remove only the stage containers/network/test volumes (this deletes synthetic DB and test manuscript storage, not source/handoff):

```bash
ssh catalystadmin@94.72.113.77 \
 'PB05_REMOVE_SYNTHETIC_TEST_DATA=YES bash "$HOME/rd014-pb05-browser-stage/scripts/PB05_STOP_TEST_STACK_ON_CONTABO.sh"'
```

The source/secrets remain in the home staging directory for controlled manual secure cleanup. Never run `docker volume prune`, replace `/app/app/main.py`, change the live Caddy route, or merge draft PR #12 as part of this test.

## Test and source integrity

Local stage acceptance: **8 tests passed** for test-only origin/host guard, two synthetic owners, secure cookie, login/logout and JSON receipt. `bash -n` passes for stage/cleanup scripts. This is a **test-only** HTTPS adapter for the existing product, not a new platform feature. The eventual production integration should mount both routers inside the existing app with the original strict production Origin, and the actual Workspace browser session. Keep the original Assignment 1 submission immutable; keep FIG-GEO01 review-only.
