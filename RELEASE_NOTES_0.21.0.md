# Sustainable Catalyst Workspace v0.21.0

## Accounts & Cloud Persistence Foundation

v0.21.0 adds optional account-bound manual cloud recovery while preserving Workspace as a free, local-first product. Guest use remains fully functional. Signing in does not upload content automatically.

### Added
- `sc-workspace-account-persistence/1.0` workspace-level persistence metadata.
- `sc-workspace-cloud-backup/1.0` explicit project-backup package.
- Authenticated REST storage using WordPress user meta, protected by WordPress REST nonces.
- Manual **Back up now**, account backup index, restore-as-new-local-copy, and explicit delete.
- SHA-256 server fingerprint, 2.5 MB/project, 25 project, and 25 MB/account guardrails.

### Boundaries
- No login wall.
- No automatic upload or background synchronization.
- Restore never overwrites an existing local project.
- No team cloud storage or institutional permissions.
- Project schema remains `sc-workspace-project/11.0`.

### Migration
Storage schema advances from 20 to 21. Existing projects and canonical object IDs are preserved; only workspace-level account-persistence metadata is added.
