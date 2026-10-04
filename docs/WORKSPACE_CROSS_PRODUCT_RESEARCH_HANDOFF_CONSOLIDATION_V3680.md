# Workspace v3.68.0 — Cross-Product Research Handoff Consolidation

v3.68.0 consolidates Research OS handoffs across Sustainable Catalyst without replacing the existing SQL-backed cross-product handoff fabric.

The existing `sc-workspace-cross-product-research-handoff-fabric/1.0` remains backend-authoritative for durable prepared handoffs, pinned scientific objects, idempotent creation, explicit destination acceptance, and durable receipts.

v3.68 adds normalized destination profiles, intent compatibility, pinned-object handoff planning, portable handoff manifests, explicit acceptance contracts, lineage across the Runtime Registry and Unified Research Sessions, and recovery-safe snapshots.

Destinations: Platform Core, Knowledge Library, Research Librarian, Workbench, Research Lab, Decision Studio, Site Intelligence, Catalyst Data, Workspace.

Safety: no automatic dispatch, destination execution, acceptance, approval, publication, evidence ranking, truth determination, or decision authority.

Migration: no database migration; no project-schema migration; rollback target v3.67.0.
