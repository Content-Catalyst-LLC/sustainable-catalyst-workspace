# RS-WXR-02 G0/G1 Packaging Handoff — 2026-10-24

**Status: PARTIAL — release NOT approved.** This branch is stacked on Reporting Studio PR #7, which depends on unmerged WXR PR #6. No merge or production change performed.

## Exact verified source baseline
- Parent candidate: `1f09292cc0b8efa28c96d31b89376c7620899c56`
- Production source identity is unverified, earlier captured Workspace runtime v3.83.0.
- Existing backend/Dockerfile copied base requirements and application source only, with no reporting Node math worker npm dependencies or optional Python PDF/SVG packages.
- Added opt-in `Dockerfile.reporting-candidate` for a multi-stage isolated image: pinned Node 26 npm-lock dependencies, Python 3.12, base + optional reportlab/svglib requirements; default `SC_WORKSPACE_REPORTING_STUDIO_ENABLED=false`; `SC_WORKSPACE_AUTO_CREATE_SCHEMA=false`.
- Local execution constraints: no `docker` executable, no PostgreSQL client/server and no live Contabo connection in this ChatGPT runtime. **The image has not yet been built or smoke-tested.**

## G1 acceptance commands (on a disposable CI / developer Docker host)

Run from repository root, pinned to this review head:

```bash
docker build --pull --file Dockerfile.reporting-candidate --tag sc-workspace-reporting:g1 .
docker run --rm --entrypoint python sc-workspace-reporting:g1 -c "import reportlab, svglib, fastapi; from app.reporting_composition import render_math; assert render_math('x^2+y^2','display').tag.endswith('svg'); print('math-ok')"
docker run --rm --entrypoint python sc-workspace-reporting:g1 -c "import os; assert os.getenv('SC_WORKSPACE_REPORTING_STUDIO_ENABLED') == 'false'; assert os.getenv('SC_WORKSPACE_AUTO_CREATE_SCHEMA') == 'false'; print('flags-ok')"
```

Keep all images/configuration off production. Record full digest and exit code. Then use isolated PostgreSQL test fixtures to rerun the four previous skipped tests, concurrent saves, strict Origin/foreign-project denial, and paired consistent DB+object-store backup/restore. Prior SQLite+object-store recovery does **not** satisfy PostgreSQL certification.

## G0 operator inventory — read-only only
From a separately authorized production access session, collect **redacted** docker image/service identifiers, PostgreSQL major version/schema fingerprint/table count, mount identities (not secrets), network routing/Caddy **hashes**, session and API health status, free storage/resources, and exact image digest. Never paste signing secrets, database passwords or raw research files into issues.

## Blocking items
- Disposable Docker image build and full scientific rendering smoke: NOT RUN.
- PostgreSQL persistence/paired restore: NOT RUN.
- Real existing-account browser acceptance in approved isolated staging: NOT RUN.
- Fresh Contabo G0 fingerprint and actual production diff: NOT VERIFIED.
- Updated GitHub Actions workflow for this candidate: NOT ADDED; repository workflow-write attempt did not succeed.
- Production owner approval: NOT GIVEN.

**Next:** build and test the candidate Dockerfile in GitHub Actions or approved isolated Docker, then attach exact-head green results; G0 on-server fingerprint only when read-only Contabo access is explicitly available. No production deployment.
