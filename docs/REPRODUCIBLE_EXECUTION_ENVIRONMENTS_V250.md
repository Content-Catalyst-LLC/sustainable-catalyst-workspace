# Workspace v2.5.0 — Reproducible Execution Environments & Dependency Manifests

Workspace v2.5.0 makes the execution environment a revisioned backend object rather than only an inline run annotation.

## Environment record

Each environment may capture:

- runtime/language versions;
- dependency manager and dependency manifest metadata;
- exact Workspace artifact revisions used as lockfiles or dependency manifests;
- container/image identity and digest metadata;
- operating-system and architecture descriptors;
- bounded hardware descriptors;
- deterministic random seeds;
- execution configuration;
- environment-variable **names only**.

Secret environment-variable values are outside the schema and are not stored by the environment registry.

## Run binding

An execution run may reference an environment by `environmentId` and optional `revision`. At run creation, the backend resolves the reference to an exact revision and stores both that resolved reference and its SHA-256 fingerprint on the run. Later environment revisions do not mutate the recorded run provenance.

The existing v2.4 inline `environment` object remains supported for compatibility and run-specific annotations.

## Reproduction boundary

v2.5.0 records the evidence needed to reproduce an environment but does not automatically create containers, install dependencies, execute arbitrary code, or capture secrets. Specialist compute remains in Lab, Workbench, and other routed Sustainable Catalyst services.
