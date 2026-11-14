# SC-CITE-01 — Operational release acceptance

**Scope:** complete two unverified gates after the previously merged 28 automated
Citation Studio tests. This work does not rerun those tests. The live gate must
reach staging Workspace **and** staging Research; the recovery gate reads
production only for off-host backup and restores to brand-new isolated Docker
resources. Neither gate itself deploys a production Research API.

## Operator prerequisites

Run on the Mac (off-host), from a checkout of this repository. Python 3.12,
SSH access to Contabo, adequate local disk space, Docker installed on Contabo,
and verified **encrypted** off-host storage are required. No secrets, backup
archives or receipt files belong in Git. The old `sc-cite01-release.sh`
download is superseded by `scripts/sc_cite01_operator.sh`.

Before operation, deploy the SC-CITE-01-enabled Workspace and Research
candidates to a **genuinely isolated** staging environment (never use the old
`studio.sh stage` command, which can mount production volumes), and prepare:

- A synthetic Workspace project and a synthetic CSL-JSON source artifact
  belonging to staging owner A, plus an existing verified public Library record.
- A staging Research area/project key and **two distinct signed staging owner
  sessions**, in both Workspace and Research.
- Four local `0600` JSON files of request headers, one for each service and
  owner. Example structure: `{"Authorization": "Bearer <REDACTED>"}` or
  `{"Cookie": "<REDACTED>"}`. Do not paste secrets into chat, logs or Git.
  File names can be arbitrary; supply their full paths.

Staging URLs must be named HTTPS staging hosts or localhost SSH tunnels; live
production URLs are refused. All synthetic identifiers must begin
`synthetic-`. Real accounts, private research and public publication are
prohibited in the integration test.

Configure these environment variables locally (values omitted deliberately):

```text
SC_CITE01_ACCEPT_STAGING=SYNTHETIC_STAGING_ONLY
SC_CITE01_RECOVERY_AUTHORIZATION=READ_ONLY_PRODUCTION_TO_OFFHOST
SC_CITE01_WORKSPACE_URL=<HTTPS staging origin or localhost tunnel>
SC_CITE01_RESEARCH_URL=<HTTPS staging origin or localhost tunnel>
SC_CITE01_SYNTHETIC_PROJECT_ID=synthetic-...
SC_CITE01_SYNTHETIC_SOURCE_ID=synthetic-...
SC_CITE01_SYNTHETIC_RESEARCH_AREA=synthetic-...
SC_CITE01_SYNTHETIC_RESEARCH_PROJECT_KEY=synthetic-...
SC_CITE01_VERIFIED_PUBLIC_LIBRARY_ID=<verified public record ID>
SC_CITE01_WS_OWNER_A_HEADERS=<mode-0600 JSON file>
SC_CITE01_WS_OWNER_B_HEADERS=<mode-0600 JSON file>
SC_CITE01_RH_OWNER_A_HEADERS=<mode-0600 JSON file>
SC_CITE01_RH_OWNER_B_HEADERS=<mode-0600 JSON file>
SC_CITE01_BACKUP_DIR=<new directory on encrypted off-host storage>
SC_CITE01_INTEGRATION_RECEIPT=<new JSON path outside Git>
SC_CITE01_SSH_TARGET=catalystadmin@94.72.113.77
```

**Single operator entry point:**

```bash
bash scripts/sc_cite01_operator.sh --check
```

This runs the live staging import/bibliography/snapshot and Research editorial
draft handoff, creates an off-host Workspace PostgreSQL dump and data-volume
archive, restores both into separate networkless containers and volumes, checks
restore inventory, deletes only generated scratch Docker resources, retains
off-host archives, and validates release-specific JSON receipts and hashes.
`--check` never replaces production.

When the preceding command returns `GO-CANDIDATE`, the named live Studio image
and candidate still match the pinned baseline, and the operator has separately
approved the Research production release and backup retention:

```bash
SC_CITE01_RECOVERY_RECEIPT="$SC_CITE01_BACKUP_DIR/sc-cite01-recovery.json" \
  bash scripts/sc_cite01_release.sh --deploy
```

The `--deploy` command requires an explicit interactive confirmation, uses
the existing protected Studio cutover script, verifies health and unauthorized
access denial, and invokes the existing rollback on post-cutover failure.
The production Research service requires its **own** deployment/acceptance
procedure; Studio cutover does not implicitly update Research.

## Receipts and limitations

The integration receipt is made only after actual HTTP calls by two distinct
staging owners and persistence/replay of a frozen bibliography in a private
Research revision. It deliberately does not publish an article or run real
production-account acceptance.

The recovery receipt is made only after files are retained **off-host**,
`pg_restore` has completed in a network-isolated scratch PostgreSQL instance,
the DB table inventory matches, and a separate scratch volume has had its
archive extracted with matching file counts. This verifies restore execution,
**not** every application's semantics or all records.

A receipt alone does not prove who ran a command: keep the CI run, off-host
storage provenance and operator record with the release. The verifier enforces
24-hour freshness and SHA-256 checks of the archived backups. If staging
configuration, signed sessions, archive isolation or restoration fails, the
release remains NO-GO. Do not create placeholder PASS receipts.

**Known production dependency:** Research production must also be promoted
through its own guarded release process before claiming the complete public
Research Hub / Citation Studio feature is live.
