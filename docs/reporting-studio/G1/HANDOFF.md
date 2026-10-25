# Reporting Studio G1 engineering handoff

**Deployment state: NOT READY; no production change or cutover.** This handoff is the continuation point for the isolated G1 candidate. It preserves, rather than replaces, `docs/research-studio/` and the private Wexford documentation handoff.

## Exact branch and dependency chain

Workspace [PR #6](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace/pull/6) `codex/wxr-09-3-complete` at `de45f37c3b1984692602ccef2f80b87a8e549094` supplies persistent private projects. [PR #7](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace/pull/7) `codex/rs-mig-01-reporting-studio` at `1f09292cc0b8efa28c96d31b89376c7620899c56` supplies the Reporting Studio route/editor. [PR #9](https://github.com/Content-Catalyst-LLC/sustainable-catalyst-workspace/pull/9) `codex/rs-wxr-02-g0-g1-packaging` at inspected `2f7e4a54e3ad7164b6ce664801fb82b2723d8b50` supplies the opt-in image/CI and a PostgreSQL smoke test. The new documentation branch is stacked on PR #9 and must be reviewed separately. None of these PRs is a production release approval.

## What works and what is not proven

Source and isolated tests support a private signed-cookie route, same-owner persistent project/artifact selection, SHA-pinned source references, immutable saved visual snapshots, strict write Origin, 409 stale-revision rejection, PDF export in the optional renderer, and cross-owner denial. [ACCEPTANCE.md](ACCEPTANCE.md) records exact commands, CI run IDs, local test output and limits. The synthetic integrated G1 acceptance test now exercises create/upload/preview/save, denial cases, logout, paired SQLite/object restore, and hash-verified reopen in one repeatable run.

There is no evidence here of a current G1 deployment, a real existing-account end-to-end flow, a retained image digest, a durable G1 `/data` mount, concurrent PostgreSQL G1 acceptance, an exact production source/image/proxy diff, or approved cutover. The older `docs/research-studio/RS_WXR_02_G0_G1_PACKAGING_HANDOFF.md` says image testing was not run; later exact-head CI did run. Preserve both records and use dates/commits to interpret them.

## Required configuration and operational boundary

The image defaults G1 off. An isolated deployment must explicitly use `SC_WORKSPACE_REPORTING_STUDIO_ENABLED=1` and existing signed-cookie/session settings; `SC_WORKSPACE_AUTO_CREATE_SCHEMA=false` must remain so schema changes are explicit. Route `/v1/private-research/persistent-projects` and route `/v1/private-research/reporting-studio` must be same-origin behind the existing auth/proxy chain. `/v1/private-research/projects` is the separate older registry and must not be used as the G1 project backend. See [IMPLEMENTATION.md](IMPLEMENTATION.md) and [DEPLOYMENT.md](DEPLOYMENT.md) for source references and storage requirements. Never place signing material, raw research, cookies or backup contents in issues or CI artifacts.

## Next executable actions

1. Run the new integrated G1 test in exact-head CI and retain its result. Add a disposable PostgreSQL 18 test for concurrent saves plus paired DB/object restore; include `test_g1_reporting_postgres.py` in the CI selection and capture the results.
2. In a separately approved isolated environment, build the exact reviewed image, retain its digest, mount a durable `/data` volume, set `SC_WORKSPACE_REPORTING_STUDIO_ENABLED=1`, and prove replacement/restart, backup/restore, browser PDF/PNG export, same-origin proxy behavior and a real existing-account login. Keep production credentials and data out of that environment unless separately authorized.
3. Perform a fresh **read-only** production source/image/auth/proxy/storage inventory, compare with the complete PR #6→#7→#9 chain, document any migration and older-image compatibility, then present the resulting release/rollback dossier for owner approval. No merge, deployment, migration, Caddy change or production restart is authorized by this documentation task.

The local G1 documentation branch touches only Markdown, the root index, one isolated test and the reporting CI test list. It does not modify application routes, data, production configuration, research files or historical documents.
