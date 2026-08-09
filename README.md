# Sustainable Catalyst Workspace

Free, public, local-first working environment for research, evidence, analysis, decisions, structured thinking, briefing, portable projects, recovery, governance, and project-bound research notebooks.

## Current release

**v0.32.0 — Research Notebook Foundation**

v0.32.0 adds the low-friction thinking layer between reading and structured Workspace objects. Projects can hold multiple notebooks with reorderable sections and working blocks for notes, sources, excerpts, questions, claims, references, checklists, dividers, and attachment references. Notebook material stays useful as working memory and moves into canonical Workspace objects only through an explicit promotion action.

The migration is non-destructive: storage advances from 27 to **28** and the project schema from `sc-workspace-project/12.0` to **`sc-workspace-project/13.0`**. Existing projects receive an empty notebook workspace while preserving objects, provenance, account backup, cross-device sync, restore points, Safe Actions, reconciliation receipts, collaboration, institutional handoffs, audit sources, and lifecycle history.

Notebook does not require AI, does not automatically run AI over notes, does not upload because a user signs in, and does not automatically promote material. Account backup, sync, restore points, and portable project export inherit the existing project boundary.

## Public product boundary

- Guest use remains fully functional and device-local.
- Accounts are optional; backup and sync remain explicit human actions.
- Research Notebook is working memory, not a second authoritative object store.
- Promoted Source, Evidence, Document, Research Question, and Research Claim records remain authoritative after promotion.
- The canonical Knowledge Library route is `/knowledge-libraries/`.
- Catalyst Intelligence remains the institutional environment for organization identity, permissions, governance, audit, shared knowledge, connectors, and deployment.

## Current schemas

- Workspace storage: **28**
- Project: **`sc-workspace-project/13.0`**
- Project export: **`sc-workspace-project-export/13.0`**
- Notebook workspace: **`sc-workspace-notebook-workspace/1.0`**
- Notebook: **`sc-workspace-notebook/1.0`**
- Notebook block: **`sc-workspace-notebook-block/1.0`**
- Notebook export: **`sc-workspace-notebook-export/1.0`**
