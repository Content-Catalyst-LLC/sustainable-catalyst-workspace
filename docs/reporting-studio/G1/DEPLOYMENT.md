# G1 isolated deployment and rollback requirements

**No production deployment is authorized by this document.** The audited source is PR #9 head `2f7e4a54e3ad7164b6ce664801fb82b2723d8b50`; PRs #6, #7 and #9 remain review branches. Production was previously observed at Workspace v3.83.0, but its exact current source/image/proxy diff has **not** been refreshed for this G1 assessment.

## Verified isolated configuration

`Dockerfile.reporting-candidate` builds a separate Python 3.12/Node 26 renderer image and defaults `SC_WORKSPACE_REPORTING_STUDIO_ENABLED=false` and `SC_WORKSPACE_AUTO_CREATE_SCHEMA=false`. The G1 route works only when the isolated runtime explicitly sets `SC_WORKSPACE_REPORTING_STUDIO_ENABLED=1`. Both `backend/scripts/reporting_isolated.py` and `backend/tests/test_g1_reporting_postgres.py` set this flag for synthetic tests. [Exact-head G1 image CI](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace/actions/runs/40131048585) built and smoke-tested the image at the audited commit; it does not prove a running isolated network service, image digest retention, mounted storage or a real-user browser workflow.

From repository root, in a disposable environment with no production credentials or mounts:

```bash
docker build --file Dockerfile.reporting-candidate --tag reporting-g1:test .
docker run --rm --entrypoint python reporting-g1:test -c "import os, reportlab, svglib; from app.reporting_composition import render_math; assert os.getenv('SC_WORKSPACE_REPORTING_STUDIO_ENABLED') == 'false'; assert render_math('x^2', 'display').tag.endswith('svg')"
```

To operate a **separate** isolated instance, configure `SC_WORKSPACE_REPORTING_STUDIO_ENABLED=1`, `SC_WORKSPACE_AUTO_CREATE_SCHEMA=false`, `SC_WORKSPACE_DATABASE_URL`, `SC_WORKSPACE_OBJECT_STORAGE_ROOT`, `SC_WORKSPACE_SESSION_SIGNING_SECRET`, `SC_WORKSPACE_SESSION_ISSUER`, `SC_WORKSPACE_SESSION_AUDIENCE`, and the existing identity-bridge dependencies. Use an isolated database and a persistent object volume. Set no secret values in shell history, logs, or Git. The origin check is hard-coded to `https://workspace.sustainablecatalyst.com`; a non-matching isolated public host requires separately reviewed route/proxy design. The loopback harness rewrites only its own synthetic test Origin; it is **not** a deployment pattern.

## Storage gate

`backend/app/config.py` defaults the object root to `/data/objects`; `Dockerfile.reporting-candidate` declares no volume or bind mount. Any `/data` inside an unmounted test container is temporary and may disappear when that container is replaced. G1 must **not** cut over until the actual database and `/data` object mount are inventoried, proven durable across replacement/restart, included as a consistent backup pair, restored into an isolated target, and checked for complete hashes and ownership. Existing WXR backup evidence in the private handoff covers an earlier production snapshot, not G1 durability certification. Do not copy research files or backup contents into this public repository.

## Prerequisites and rollback

The existing signed-cookie identity bridge, persistent-project schema, object store, same-origin `/v1` proxy, and optional renderer dependencies are prerequisites. G1 introduces no new DDL, but the stacked WXR persistent-project prerequisite and its migration status must be verified against the live database before any approved cutover. Back up the live database **and** object root consistently and verify restoration before changing any service. Record exact current image digest and proxy hash first. Rollback is to disable `SC_WORKSPACE_REPORTING_STUDIO_ENABLED` or restore the preserved image/configuration **only after** confirming that older code can read projects containing G1 report objects; retain the additive revisions and blobs. Never delete new research to make rollback appear clean. A production rollback rehearsal on a restored clone remains BLOCKED pending durable storage and owner deployment approval.
