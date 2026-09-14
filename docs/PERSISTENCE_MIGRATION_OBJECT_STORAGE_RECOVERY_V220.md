# Workspace v2.2.0 — Persistence Migration, Object Storage & Recovery Hardening

## Migration safety model

Migration is explicit and two-phase:

1. `plan` enumerates the current user's legacy WordPress project/notebook records and compares them with backend heads.
2. `apply` is accepted only when the plan contains no divergent backend records.

Identical records are skipped. Divergent records produce a conflict and nothing is imported. The source `user_meta` records remain untouched after successful migration. A deterministic receipt makes repeat application idempotent.

## Artifact storage

Artifact content is decoded server-side, SHA-256 hashed, and atomically written beneath `/data/objects/sha256/<prefix>/<digest>`. PostgreSQL stores user-scoped artifact metadata and revision history. The Docker volume is named `sc-workspace-data` so backend directory replacement does not remove blobs.

## Recovery snapshots

A recovery snapshot captures the current server-side head metadata for projects, notebooks, and artifacts plus a SHA-256 fingerprint of the manifest. It does not duplicate blob bytes. Snapshots are bounded per account; oldest snapshots are retired when the configured cap is exceeded.

## Boundaries

v2.2.0 does not add background jobs, compute orchestration, live collaboration, server-side project authorship, or automatic WordPress-store deletion.
