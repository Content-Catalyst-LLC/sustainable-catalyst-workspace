# Sustainable Catalyst Workspace Backend v2.2.0

Workspace v2.2.0 hardens the dedicated FastAPI + PostgreSQL persistence plane introduced in v2.1.0.

## Added in v2.2.0

- non-destructive WordPress `user_meta` migration planning and apply endpoints
- deterministic migration receipts and idempotent replay detection
- source revision preservation for imported project and notebook heads
- content-addressed artifact storage using SHA-256
- persistent Docker volume for artifact blobs
- artifact revision preconditions and metadata history
- artifact storage integrity verification
- bounded recovery snapshots of project, notebook, and artifact heads

## Preserved

Workspace remains local-first. Browser-local projects remain canonical. Migration never deletes the legacy WordPress store, and the WordPress bridge can plan/apply migration while backend mode is still disabled. Explicit backup/sync semantics remain unchanged.

## Runtime

The service listens on container port `8089`. The example production mapping uses VPS loopback port `8094` because `8089` is already allocated to Decision Studio in the Sustainable Catalyst VPS layout.

The service remains private: browser-direct access is not supported. WordPress sends the service token and user scope.

## Storage

PostgreSQL stores project/notebook heads, revisions, migration receipts, artifact metadata, artifact revisions, and recovery manifests. Artifact bytes are written to `/data/objects` in a persistent Docker volume using paths derived from SHA-256 digests.

Blob deletion is intentionally conservative in v2.2.0: deleting an artifact removes its Workspace metadata/revisions but leaves content-addressed bytes for later garbage-collection tooling, avoiding accidental removal of shared/referenced blobs.
