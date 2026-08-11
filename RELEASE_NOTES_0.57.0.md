# Sustainable Catalyst Workspace v0.57.0 — Institutional Research Packages

## Purpose
Create deliberate institutional research handoff bundles from selected Workspace material without publishing the Workspace or changing the source project.

## Added
- Explicit project and Integrated Knowledge record scope.
- Frozen package snapshots with deterministic integrity fingerprints.
- Optional full selected content, recorded provenance, related Citation Library references, Research Tasks, and Collaboration review context.
- Disclosure manifest showing scope, included context, counts, and deliberately omitted local/device state.
- Browser-local package ledger, export, and package-file verification.
- Public contract endpoint: `/wp-json/sc-workspace/v1/institutional-research-packages-contract`.

## Governance
Package creation is an explicit disclosure action. Workspace does not upload, publish, refresh, mutate canonical research, or establish institutional permissions automatically. The v0.19 Catalyst Intelligence promotion/receipt workflow remains available as a compatibility path.

## Schema
Storage remains 35; Project remains `sc-workspace-project/20.0`; Project Export remains `sc-workspace-project-export/20.0`; Notebook Workspace remains `8.0`.
