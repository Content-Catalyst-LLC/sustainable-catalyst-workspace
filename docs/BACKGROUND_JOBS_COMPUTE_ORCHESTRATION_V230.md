# Workspace v2.3.0 Background Jobs & Compute Orchestration

The Workspace backend now contains a durable queue and a separate worker process. API requests create or inspect jobs; the worker claims queued jobs using PostgreSQL row locking and records state transitions as immutable events.

## Job lifecycle

`queued -> running -> succeeded`

Failure may produce `queued` again while attempts remain, then `failed`. Missing cross-product route configuration produces `blocked` instead of repeated failures. Queued/blocked work may be cancelled. Failed/blocked/cancelled work may be explicitly retried.

## Cross-product routing

The request chooses only a named target product and operation. It cannot choose a URL. The worker resolves the target through server environment variables and emits `sc-workspace-compute-handoff/1.0`.

Supported registry names are `core`, `lab`, `workbench`, `decision-studio`, `library`, and `site-intelligence`. Each route is independently configured. No downstream endpoint is invented by Workspace.

## Deliberate exclusions

This release does not add predictive models, scientific compute, WebSocket streaming, automatic cross-product approval, or a universal downstream execution endpoint. Those require later product-specific contracts.
