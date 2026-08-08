# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free public working environment across the Sustainable Catalyst platform.

## Current release

**v0.4.1 — Research Workspace

Workspace Projects can now contain typed, reusable objects: sources, evidence, datasets, analyses, decisions, documents, and exports. Each object has a stable ID, lifecycle state, tags, provenance fields, timestamps, and local export support.

## WordPress

Primary shortcode:

```text
[sc_workspace]
```

Compact Platform entry:

```text
[sc_workspace_entry]
```

Canonical route:

```text
/platform/workspace/
```

## Persistence boundary

Projects and their objects are stored in the current browser only. v0.4.1 does not create an account, upload project/object content to Sustainable Catalyst, synchronize between devices, or introduce collaboration.

## Object model

Supported object types:

- Source
- Evidence
- Dataset
- Analysis
- Decision
- Document
- Export

Project schema: `sc-workspace-project/2.0`  
Object schema: `sc-workspace-object/1.0`  
Storage schema: `3`

## Product Registry

- Canonical ID: `sustainable-catalyst-workspace`
- Family: `commercial`
- Console screen: `commercial`
- Display order: `400`
- Lifecycle: `experimental`
- Access: free public
- Canonical repository: `Content-Catalyst-LLC/sustainable-catalyst-workspace`


## v0.4.1 Research Workspace
Research questions, source capture, reading queues, evidence extraction, claims, and evidence links now operate directly on the local Workspace Object model. See `docs/RESEARCH_WORKSPACE_V040.md`.


## v0.4.1 identity boundary
Workspace remains guest-accessible and device-local. Existing WordPress accounts may be recognized for session identity, but signing in does not upload or synchronize projects. See `docs/IDENTITY_ACCOUNTS_PERSISTENCE_BOUNDARY_V041.md`.
