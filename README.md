# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free public working environment across the Sustainable Catalyst platform.

## Current release

**v0.6.0 — Decision Workspace**

Workspace now supports two first-class working modes inside a persistent Project:

- Research Workspace — questions, sources, reading queues, evidence, and claims.
- Decision Workspace — analytical questions, datasets, variables, assumptions, methods, comparisons, and findings.

Both modes operate on the same portable Workspace Object model rather than creating isolated product-specific artifacts.

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

Workspace remains usable without signing in. Projects and objects are stored on the current device. Optional WordPress authentication identifies the current account session only; v0.6.0 does not upload, claim, or synchronize local project content.

## Contracts

- Project: `sc-workspace-project/5.0`
- Object: `sc-workspace-object/1.0`
- Research: `sc-workspace-research/1.0`
- Analysis: `sc-workspace-analysis/1.0`
- Identity: `sc-workspace-identity/1.0`
- Storage schema: `6`

## Object model

Supported object types: Source, Evidence, Dataset, Analysis, Decision, Document, and Export.

## Product Registry

- Canonical ID: `sustainable-catalyst-workspace`
- Family: `commercial`
- Console screen: `commercial`
- Display order: `400`
- Lifecycle: `experimental`
- Access: free public
- Canonical repository: `Content-Catalyst-LLC/sustainable-catalyst-workspace`

See `docs/ANALYSIS_WORKSPACE_V050.md` for the v0.6.0 analytical contract.


## v0.6.0
Decision Workspace adds structured decisions, options, criteria, assessments, risks, final rationale, confidence, and canonical Decision objects.
