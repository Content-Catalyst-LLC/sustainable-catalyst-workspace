# Workspace v2.32.0 — Unified Scientific Object API

Workspace v2.32.0 introduces one backend-authoritative scientific-object projection over the scientific registries already present in Workspace. Artifacts, datasets, models, parameter sets, execution runs, execution environments, runtime adapters, scientific study packages, visualization specifications, and scientific receipts now share one canonical discovery and identity contract.

The unified API provides typed discovery, project scoping, text filtering, canonical object lookup, revision or event history, and explicit provenance relationships. Each normalized object carries kind, object ID, project ID, canonical revision when applicable, source fingerprint, deterministic object fingerprint, timestamps, summary metadata, and capability flags.

The generic scientific-object surface is intentionally read-only. It does not introduce a generic mutation endpoint. Canonical writes continue through the existing bounded domain APIs, preserving revision checks, local-first synchronization, provenance, policy, and receipt behavior.

No new database migration is required. Migration lineage remains through `029_local_first_synchronization_protocol.sql`. The v2.28.1 interaction repair, v2.29 typed WordPress proxy, v2.30 thin-client state boundary, and v2.31 local-first synchronization protocol remain intact.
