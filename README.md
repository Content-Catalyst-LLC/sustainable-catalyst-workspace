# Sustainable Catalyst Workspace v0.67.0

## Cross-Device Continuity & Sync Hardening

Free public, local-first research workspace with explicit account backup and conflict-safe cross-device continuity. v0.67.0 adds retry-safe sync operation IDs, interrupted-operation reconciliation, sync-safety restore points before cloud pulls, explicit device-migration packages that import as new local copies, duplicate migration guards, and a server boundary preventing manual backup from overwriting an active sync head.

Storage schema remains 35 and Project schema remains `sc-workspace-project/20.0`. No automatic or background synchronization is introduced.
