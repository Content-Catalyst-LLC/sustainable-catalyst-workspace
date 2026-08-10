# Sustainable Catalyst Workspace v0.48.0 — Cross-Project Knowledge

## Purpose
Allow one Workspace project to reuse research owned by another project without copying the canonical record or changing ownership.

## Added
- Browser-local Cross-Project Knowledge reference ledger.
- Explicit target project, canonical source pointer, relationship label, and context note.
- Supported explicit relationships: references, supports, informs, extends, contrasts, related.
- Unresolved reference visibility when a source or target project is unavailable on the device.
- Cross-project reference export/import with deterministic integrity fingerprints.
- Research Graph integration: target projects connect to referenced research only through explicit recorded cross-project edges.
- Public `/cross-project-knowledge-contract` capability contract.

## Governance boundary
Cross-project references do not copy source content, transfer ownership, create a duplicate canonical knowledge store, infer semantic relationships, invoke AI, or mutate source/target projects. Same-project references are rejected by this layer because project-local relationships already have canonical mechanisms.

## Compatibility
Storage remains 35. Project remains `sc-workspace-project/20.0`. Project Export remains `sc-workspace-project-export/20.0`. Knowledge Graph remains `sc-workspace-knowledge-graph/2.0`. The 4px editorial header rule introduced in v0.46.1 is retained.
