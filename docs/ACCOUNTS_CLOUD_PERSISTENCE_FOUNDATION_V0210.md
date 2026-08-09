# Accounts & Cloud Persistence Foundation — v0.21.0

Workspace remains local-first and anonymous-capable. Cloud persistence is an explicit recovery feature for authenticated WordPress accounts, not a hidden synchronization layer.

## Flow
1. Work locally as guest or signed-in user.
2. Sign in only when account recovery is useful.
3. Choose a local project and select **Back up now**.
4. Workspace sends that one backup package through authenticated same-origin WordPress REST.
5. Restore creates a new local copy; it never overwrites the source project.

## Storage
Server backups are stored per WordPress user in private user meta under `sc_workspace_cloud_projects_v1`. The API returns metadata separately from project content. WordPress cookie authentication plus `X-WP-Nonce` protects write/read operations.

## Guardrails
- 25 projects/account
- 2.5 MB/project
- 25 MB/account
- SHA-256 package fingerprint
- no background sync
- no automatic upload on sign-in
- no team or institutional storage semantics
