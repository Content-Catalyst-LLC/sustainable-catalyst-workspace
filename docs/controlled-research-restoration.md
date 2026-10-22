# Controlled research restoration in Workspace

This feature extends the existing FastAPI Workspace, signed browser session, user/project registry, artifact store and revision history. It provides a private research area, a deterministic preflight, selective structured-record/document restoration, server-owned audit receipts, and target-only rollback. It creates no credential store, standalone application or database service. **It is not deployed or enabled in production.**

## Source baseline and dependency

Observed production API/config version: **3.83.0**. The GitHub main source at the time of inspection is `fb932c18f4f88985297ef770128157795a5892f8`. The existing identity/recovery overlay branch is `a7206e22122229d5ef4fe46b41fe7664794daa84` (Workspace PR #2). This PR is stacked on that branch and must be reviewed after it; it does not pretend the live deployment equals bare main.

The observed running image is `sustainable-catalyst-workspace:wxr-private-review-20261022T195256Z`, image ID `sha256:f764de0bbb28d009c352d900d6676e51366855d072255db4e44a5818e39dea72`. The deployed review adapter SHA-256 is `1a5848d654c239a49e387921c60549ac1a8ccfb32a7786b06ed28a21fed6ca20`; the existing ERW identity bridge is `dfd9be00615cd08e47712540453b2425f3c4b20c94ee8f6dc1e28d75b26b151c`. The image has no verified OCI source revision and some pre-existing private identity files are absent from main/PR #2. **Complete source/overlay reconciliation is a deployment prerequisite.** No production rebuild from an older main branch is authorized.

The older WXR staging package is not a native restoration mechanism: it copies a review catalog/journal, depends on a caller-authorized operator decision, and expects `id` fields where the actual catalog uses project_id/record_id. Its fallback index IDs must not replace original identities. This feature reuses Workspace's actual persistence APIs instead of activating that package or another recovery server.

## API contract

All responses are private/no-store/noindex. A signed Workspace browser cookie is required; browser identity headers and arbitrary bearer values cannot establish a subject. No operation accepts a source path, owner ID, role or record body from the browser.

| Method/path under `/v1/private-research/recovery` | Behavior |
|---|---|
| GET `/ui` | Native private research area shell, safe DOM rendering and hashed-script CSP; no embedded research inventory |
| GET `/area-status` | Resolves the server-configured, subject-bound selection; returns owned target research objects/manifests and preflight |
| POST `/area` | Creates an empty private research area using the existing revision-checked project API; requires explicit create-area authorization and write enablement; existing projects are not overwritten |
| GET `/plan?source_project_id=...&target_project_id=...` | Read-only deterministic plan for the exact source/target grant and selected record IDs; requires an existing owned target |
| POST `/restore` | Revalidates approval, source/bundle/blob hashes, target ownership/revision, backup files, source ownership and environment dependencies; restores eligible records while unrelated blocked records remain restricted |
| POST `/rollback` | Requires current authorization and expected revision; removes only unchanged objects/artifact metadata named in the server-owned batch receipt; preserves originals, audit and revisions |
| GET `/artifacts/{artifact_id}` | Hash-verifies native artifact bytes and enforces subject + target project + restored object reference; attachment-only with sandbox CSP |

Restore request (synthetic):

```json
{"source_project_id":"synthetic-source","target_project_id":"synthetic-target","plan_sha256":"<64 lowercase hex>","expected_revision":1}
```

Rollback adds `batch_id`, the server-returned `recovery-<40 hex>` identifier, and uses the current target revision. Area creation takes only source_project_id and target_project_id. Unknown request fields are rejected. Write requests also require exact allowed Origin and `X-Recovery-Intent: create-area`, `restore` or `rollback` as appropriate.

The semantic plan includes pinned catalog/bundle hashes, current target revision/fingerprint, original identifiers, classifications and per-record blockers. Input ordering does not change identity. Classifications include MATCHED, UNMATCHED, AMBIGUOUS, DUPLICATE and BLOCKED. Identical duplicate observations do not create duplicate target objects; ambiguous variants never choose a target silently. A matched destination object must have exactly equal preserved payload/provenance. Conflicts are restricted, not overwritten.

## Authorization and activation configuration

`SC_WORKSPACE_CONTROLLED_RECOVERY_ENABLED` defaults off. It must equal `true` to allow any create/restore/rollback. No file or permission is created automatically. Production enabling is a separate explicit approval, not a consequence of merging this PR.

Server-only inputs:

- `SC_WORKSPACE_RECOVERY_AUTHORIZATION_FILE`: absolute, protected regular JSON file (0600, trusted owner). Contains exact schema/subject SHA-256/source project/target project/record IDs, catalog+bundle hashes, issued_at/expires_at (maximum 24 hours), allowed_actions, approved_plan_sha256, ownership evidence digest/reference, environment_bindings, and backup_restore_evidence_sha256. No client role, Boolean ownership assertion or review-only grant authorizes restoration.
- Authorization schema: `sc.workspace.controlled-recovery-authorization.v1`. Exact keys are enforced by `_context`. Before plan approval, approved_plan_sha256 may be null; actual restoration requires the reviewed semantic plan hash. An approval record is a protected administrative decision/evidence binding, not a new authentication system. Administrators must validate the underlying evidence; a file field is not independent proof.
- `SC_WORKSPACE_RECOVERY_CATALOG_FILE` and `SC_WORKSPACE_RECOVERY_BUNDLE_FILE`: absolute regular, read-only source snapshots pinned by the authorization. Bundle schema is `sc.workspace.controlled-recovery-source.v1`, with catalog_sha256 and records. Each record preserves record_id/project_id/owner_fingerprint/payload/payload_sha256, and original timestamps/calculation hash when supplied. Bundle files and private snapshots must never be committed or uploaded to public CI.
- `SC_WORKSPACE_RECOVERY_BLOB_ROOT`: protected directory of immutable source blobs named by SHA-256. Optional document descriptors preserve blob_sha256/blob_size_bytes/filename/media_type. Original PDF/Word source hashes inside the payload must equal the descriptor. No browser-supplied filesystem paths or network fetches.
- `SC_WORKSPACE_RECOVERY_BACKUP_MANIFEST_FILE` and `SC_WORKSPACE_RECOVERY_BACKUP_ROOT`: protected, digest-bound evidence plus actual backup files. Schema `sc.workspace.recovery-backup-verification.v1` lists relative_path/sha256, database_backup_sha256 and restore_rehearsal_evidence_sha256. Restore verifies every listed file and coverage for catalog/bundle/selected document blobs. The rehearsal evidence must come from a real independent restore check before production approval. Runtime does not execute a database restore or trust an unverified backup Boolean.
- `SC_WORKSPACE_RECOVERY_ALLOWED_ORIGIN`: defaults to the existing Workspace origin. Do not loosen it to `*`.

Keep configuration directories protected and outside user uploads, with no untrusted symlink ancestors. Missing, invalid, expired, wrong-subject, wrong-project, changed or insecure authorization denies access. Existing legacy private review access is not repurposed into restoration access.

Source-owner association follows the existing ERW bridge contract: the signed subject is `erw:` plus the verified Workbench owner; its historical owner fingerprint must match the source project and calculation. A protected review approval cannot override a different source owner. Targets are always looked up by the existing `(user_key, project_id)` registry key; there is no cross-user target fallback. Existing sync writers and restoration share a row lock before checking the revision, preventing concurrent lost updates on PostgreSQL.

## Scope and research experience

Restoration copies approved source payloads into ordinary private Workspace project objects as `recovered-research-record`, preserving source namespaces, original IDs, owner fingerprints, hashes, timestamps and provenance. It does not recalculate results, certify science, rewrite historical owners or publish anything. Original project identities remain distinct within the coherent target area. Gate/development projects are blocked from the research target; they remain in the restricted source collection pending a separately reviewed development collection.

Environment records with unresolved associations remain unlinked. A dependent calculation needs an evidence-bound environment mapping. An explicitly declared independent record with no actual environment references can restore without inventing a link to an unrelated environment. Source documents can therefore progress without resolving every historical environment.

The private area shows restored calculation/source metadata and offers authenticated original document downloads. Existing Workbench/reporting, Library, Lab and Site Intelligence entry points are linked; opening a tool does not dispatch execution or import evidence. Native verified cross-product model/figure execution, citation identity assessment, editable manuscript composition and full research replay remain separate integration work. Do not describe links as completed data integrations.

Unassigned/unowned figures and research-environment artifacts cannot be promoted merely because their hashes verify. They remain in the protected recovery archive, not an account-accessible project. Eligible owned records proceed even when other selected records remain BLOCKED. There is no claim that all historical records can be safely restored to the current account.

## Migration, transaction and rollback boundaries

Migration `051_controlled_research_restoration.sql` adds one audit table in the existing database; it does not touch source stores or move research data. It requires reviewed backup/restore evidence and separate deployment/migration approval. Existing `auto_create_schema` policy is unchanged.

Restore acquires the owned target row, rechecks the plan/revision, verifies backup/blob bytes, creates native ArtifactHead/ArtifactRevision rows without independent commits, appends project objects and a **server-owned** RecoveryRestorationReceipt, then commits through the existing project store once. Client-editable project traceability is only an audit mirror, never rollback authority. A forged sync operation ID cannot manufacture success. A persistence failure rolls back all database changes. Content-addressed blob files may remain orphaned after failure; they are not exposed without authorized DB metadata and are deliberately not deleted because blobs can be shared.

Rollback verifies the server receipt and unchanged restored object hashes, artifact revisions, batch provenance and target membership. It removes only batch-created object references/artifact metadata, records a new project revision, and marks the receipt ROLLED_BACK. It retains original sources, earlier Workspace revisions, backup files and immutable content-addressed bytes. Changed recovered objects require human review rather than automatic deletion. Rollback needs current authorization but not the continuing presence of source files.

Application rollback: disable the feature flag first, revert the candidate image/config through the reviewed release mechanism, and retain the additive receipt table/audit. A service rollback is not a data rollback. No destructive down-migration or broad filesystem cleanup is provided.

## Validation

New tests cover authenticated source/target isolation, wrong owner/grant, malformed/source/blob integrity failures, missing ownership/environment evidence, matched/duplicate/ambiguous/blocked records, deterministic plans, zero-write GETs, native document restore/download, partial restoration, backup corruption, atomic failures, idempotency, scoped rollback and hostile client metadata. Tests use synthetic fixtures only.

The GitHub workflow runs PostgreSQL 18 in an ephemeral service, takes real `pg_dump` snapshots and restores them to an isolated rehearsal database, exercises concurrent restore/sync writers and applies the additive migration twice. Existing identity/domain/sync/handoff/portable-recovery regressions run separately. A stale sync-test version allowlist was updated to a supported minimum contract version and current app health version; the client contract's separately advertised version remains unchanged.

Local PostgreSQL startup was denied by the workstation sandbox's shared-memory policy; local SQLite tests are not presented as PostgreSQL concurrency certification. Final counts and CI run evidence belong in the PR, not fabricated production acceptance. No production source, record, permission, credential, firewall or running service was modified.
