# Workspace v2.4.0 — Dataset, Model & Execution Run Registry

Workspace v2.4.0 adds a durable provenance-aware registry above the v2.3.0 background-job and orchestration plane.

## Registry objects

- **Dataset records** — revisioned descriptors for tables, time series, geospatial data, documents, generated data, external sources, and artifact-backed data.
- **Model records** — revisioned analytical-model descriptors with framework, algorithm, configuration, input/output schemas, lineage, source artifact, and optional server-side execution route metadata.
- **Parameter sets** — revisioned named parameter collections that can be bound to models and frozen into execution runs.
- **Execution runs** — durable run identities that resolve datasets, models, and parameter sets to exact revisions and fingerprints when the run is created.
- **Run events** — append-only lifecycle observations for creation, job linkage, worker state changes, and output registration.
- **Run outputs** — links to Workspace artifacts or externally identified SHA-256 outputs.

## Reproducibility model

Creating a run resolves every referenced registry object to an exact revision and fingerprint. Those resolved references, the execution target/operation, and the declared environment form a deterministic SHA-256 **input fingerprint**. Registered outputs are then folded into a second **reproducibility fingerprint**.

Later edits to a dataset, model, or parameter set do not silently rewrite an existing run's frozen provenance.

## Job integration

A v2.3.0 job request may now include `executionRunId`. The durable worker propagates queued/running/succeeded/failed/blocked/cancelled job state into the linked run. Workspace still orchestrates specialist products rather than duplicating their compute engines.

## Non-goals

v2.4.0 does not automatically train models, select models, infer that a model is scientifically valid, execute arbitrary user-supplied URLs, or declare a run reproducible merely because it has a fingerprint. The registry records provenance and execution state; scientific validity remains a separate review concern.
