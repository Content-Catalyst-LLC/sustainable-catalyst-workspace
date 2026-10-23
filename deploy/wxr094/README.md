# WXR-09.4 isolated release engineering

This directory is a review-only release package. No command here authorizes a
production deployment, backup, migration, or service restart.

## Startup and schema

`backend/Dockerfile` starts `uvicorn` directly. `python -m app.init_db` is a
separate explicit schema-maintenance command; never run it against production
under the current no-migration authorization. Keep
`SC_WORKSPACE_AUTO_CREATE_SCHEMA=false`. The only model added beyond the
deployed v3.83.0 source is `workspace_recovery_restoration_receipts`; the
controlled-recovery feature is outside this release. The persistent Wexford
router uses the existing `workspace_project_*` and `workspace_artifact_*`
tables and `/data/objects`. Verify their exact DDL on a restored copy before
release; no production schema inspection or migration was performed here.

CI builds the candidate with:

```sh
source_commit=$(git rev-parse HEAD)
docker build --pull --file backend/Dockerfile --tag wxr-09-4-candidate:${source_commit} backend
docker image inspect --format='{{.Id}}' wxr-09-4-candidate:${source_commit}
```

The CI test starts that image against an **empty isolated PostgreSQL 18
database** with schema creation disabled and verifies it creates zero tables.
It then validates and exercises `Caddyfile.isolated` against the candidate
backend. This fixture mirrors the existing session/private-research matchers
plus the proposed narrow project/artifact routes; it is not the live Caddyfile.

## Paired backup tool

`backend/tools/wxr_release_backup.py` captures a PostgreSQL custom-format dump
and a complete object-root archive. It writes a manifest with SHA-256 hashes
for both components and every object. It refuses capture unless the operator
asserts that **all writers are quiesced**. PostgreSQL and filesystem storage
cannot otherwise form a consistent point-in-time pair. This assertion must be
supported by an approved operational procedure; the tool does not quiesce or
restart anything. The database URL is read from
`SC_WXR_RELEASE_DATABASE_URL`, never passed on the command line. Use
PostgreSQL 18 `pg_dump`/`pg_restore` for the current archive format. The
optional `SC_WXR_PG_CONTAINER` selects PostgreSQL 18 clients in an isolated
Docker container, as in CI. Do not put backup outputs in Git or CI artifacts.

Example for an approved **isolated** environment, with the URL set privately:

```sh
python backend/tools/wxr_release_backup.py capture \
  --object-root /isolated/objects --destination /isolated/paired-backup \
  --confirm-writes-quiesced
python backend/tools/wxr_release_backup.py verify --source /isolated/paired-backup
python backend/tools/wxr_release_backup.py restore \
  --source /isolated/paired-backup \
  --object-destination /isolated/restored-objects
```

Restore is hard-limited to a local database named `sc_wxr094_restore*` and a
new, absent object destination. Create that empty database first. If a restore
fails, retain the partial isolated database and directory for diagnosis;
discard them only after recording the failure. The tool checks archive paths,
component hashes, PostgreSQL archive readability and restored object hashes.
It does not claim to verify application-level ownership, project associations,
or source scientific claims; those require the integration checks below.

## Non-destructive scientific import

The private documentation repo's `docs/wexford/SCIENTIFIC_FILE_MANIFEST.json`
describes 69 local research files. A 23 October read-only check found all 69
present with matching size and SHA-256 (19,425,901 bytes total; largest
7,712,115 bytes). None was copied to this repository. The upload allowlist now
covers every extension in that manifest, including GeoJSON, HTML, Python,
compiled Python and RIS. Downloads use `application/octet-stream`, attachment
disposition, and a sandbox CSP. Before approved live import, create a private
project under the existing signed-in owner, upload a copy of the original
manifest as a research file, then upload each original byte sequence once.
Verify each returned and downloaded SHA-256 against the manifest, preserve the
manifest's relative source path/association as the provenance record, and leave
historical recovery records untouched. The current upload API stores filename,
hash, project association and source type; it does **not** store a structured
per-file historical source ID or citation relation. Those remain in the
manifest until a separately reviewed metadata feature exists. No live import
is authorized here.

## Release and rollback gates

Keep the verified production identity/recovery overlays, worker image,
PostgreSQL volume, `sc-workspace-data` volume, recovery catalog bind, and
existing `/erw` forward-auth. Add only the `/v1/user-workspace*`,
`/v1/projects*` and `/v1/artifacts*` Caddy matchers shown in the private
Wexford readiness handoff; existing `/v1/session*` and
`/v1/private-research*` matchers already reach the backend. Stage/validate the
complete Caddyfile and preserve its original hash before an approved reload.

Before asking for production authorization: obtain an approved *current*
paired PostgreSQL/object backup and independent copy; prove isolated restore,
owner/row and object-hash checks; test old-image rollback on the restored copy;
pin the candidate source commit and actual promoted image digest. On failed
acceptance, restore old image, static config and Caddyfile while retaining
database and object volumes. A paired data rollback needs a separate data-loss
review and explicit approval. Live acceptance must test existing ERW login,
private project create/open, all required file formats, SHA-256 download,
logout/relogin/restart, cross-user/project denial and unchanged recovery routes.
