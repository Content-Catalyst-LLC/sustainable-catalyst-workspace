# Sustainable Catalyst Workspace Backend v2.5.0

Workspace v2.5.0 extends the durable job/run registry with revisioned reproducible execution environments.

## Added in v2.5.0

- revisioned execution-environment registry
- runtime/language version descriptors
- dependency manifests and exact lock-artifact references
- container/image identity descriptors
- OS/architecture and bounded hardware metadata
- random-seed capture
- environment-variable **names only**; secret values are never part of the contract
- execution runs pin environment id, exact revision, and SHA-256 environment fingerprint
- compatibility with the v2.4 inline `environment` field

## Environment endpoints

- `GET/POST /v1/execution-environments`
- `GET /v1/execution-environments/{environment_id}`
- `GET /v1/execution-environments/{environment_id}/revisions`
- `GET /v1/execution-environments/{environment_id}/revisions/{revision}`

Runs may use `environmentRef: {"environmentId":"...","revision":N}`. The backend resolves and freezes the exact environment fingerprint at run creation.
