# Workspace v2.32.0 — Unified Scientific Object API

## Contract

The API schema is `sc-workspace-scientific-object-api/1.0`; normalized objects use `sc-workspace-scientific-object/1.0`. PostgreSQL/Python remains canonical. Browser projections are memory-only and discardable.

Supported kinds: artifact, dataset, model, parameter-set, execution-run, execution-environment, runtime-adapter, study-package, visualization-spec, scientific-receipt.

Endpoints: profile; unified index/discovery; canonical object lookup; revision/event history; relation projection.

Relations expose bounded provenance edges such as dataset → artifact, model → source artifact, parameter set → model, execution run → datasets/model/parameters/environment/adapter/output artifacts, environment → lock artifacts, study package → bundle artifact, and visualization → source objects.

There is no generic mutation endpoint. Existing bounded APIs remain authoritative for all writes.
