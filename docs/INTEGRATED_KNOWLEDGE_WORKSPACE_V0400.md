# Integrated Knowledge Workspace — v0.40.0

Workspace v0.40.0 consolidates Research Notebook, Personal Knowledge, and Research Workspace into one research entry point without replacing their canonical data models.

## Unified derived index
The Integrated Knowledge Workspace derives records at runtime from canonical Workspace Objects, Research Notebook notebooks/blocks, and Research Workspace questions/claims. The index is not persisted as a duplicate content database.

## Canonical origin handoff
Every result carries a stable origin reference and can be opened back in the surface that owns it: a Workspace Object, Research Notebook, or project Research Workspace.

## Explicit connections
The inspector surfaces only relationships already recorded in Notebook links or Research evidence/claim records. No semantic relationship is invented merely because two items look similar.

## Governance boundary
The integrated layer runs no automatic AI, semantic embeddings, source mutation, or background network activity. Existing Notebook assistance, sync, review, reconciliation, audit, and provenance boundaries remain unchanged.

## Schema strategy
v0.40.0 is intentionally schema-stable at storage 35, Project 20.0, Project Export 20.0, and Notebook Workspace/Export 8.0. Consolidation does not require rewriting canonical project data.
