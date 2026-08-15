# Workspace v1.11.0 — Developer API, SDK & Extension Contracts

Workspace v1.11.0 establishes a stable, versioned extension boundary for Sustainable Catalyst Workspace.

The Developer API is read-only and descriptive by default. Extensions declare a manifest and request only named capabilities. A user-approved capability grant is a portable governance record; it is not an authentication credential and does not authorize arbitrary code execution or hidden server mutation.

## Stable contract families

- Workspace objects
- Universal Search
- Library continuity
- Knowledge Graph
- Lab handoffs
- Workbench and Decision Studio round trips
- Cross-device continuity
- Review Rooms
- Institutional Audit
- Research Operations

## Capability model

The v1 contract exposes ten declared capabilities: project summary, Workspace objects, Universal Search, Library pointers, Knowledge Graph, handoff context, Review Rooms, audit dossiers, Research Operations, and portable-envelope creation.

No mutating REST endpoints are introduced. There is no dynamic plugin installation, remote extension loading, automatic network access, automatic canonical mutation, automatic AI, behavioral telemetry, query telemetry, secrets in manifests, or tokens in URLs.

## Compatibility

The public API namespace remains `sc-workspace/v1`. Additive changes may occur within v1; breaking changes require a new major API contract. Storage remains schema 35 and project/export schemas remain 20.0.
