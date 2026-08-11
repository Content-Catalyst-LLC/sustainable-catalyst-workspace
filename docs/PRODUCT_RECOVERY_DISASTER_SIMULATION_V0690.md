# Product Recovery & Disaster Simulation — v0.69.0

v0.69.0 turns the recovery architecture into an explicit, repeatable drill suite. The simulator uses isolated in-memory fixtures; it does not damage live Workspace data in order to prove recovery behavior.

## Scenarios

1. Corrupt canonical state — unreadable bytes are detected and left untouched for review.
2. Interrupted write — a staged journal can reconcile to the pre-write canonical state without guessing.
3. Storage exhaustion — a refused write cannot be reported as a verified save, and prior canonical bytes remain intact.
4. Malformed import — partial or malformed project envelopes are blocked before commit.
5. Stale restore point — restore semantics remain new-local-copy and leave the source project independent.
6. Sync revision conflict — stale and remote revision facts remain explicit; no silent last-write-wins resolution is introduced.
7. Missing reference — unresolved references remain unresolved rather than being silently substituted.
8. Future version mismatch — unsupported future project schemas are blocked; Workspace does not guess a downgrade.

## Governance boundary

The drill engine performs no canonical mutation, automatic repair, automatic restore, automatic import commit, automatic sync, background network request, telemetry submission, or production-data fault injection. Reports are metadata-only and contain scenario outcomes rather than project content.

Storage remains 35 and Project remains `sc-workspace-project/20.0`.
