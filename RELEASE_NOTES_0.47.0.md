# Sustainable Catalyst Workspace v0.47.0 — Research Graph & Relationship Explorer

## Added
- Research Graph v2 across canonical Workspace objects, Notebook material, research questions/claims, Citation Library references, Notebook promotions and syntheses.
- Explicit notebook links/backlinks rendered as graph edges.
- Promotion and synthesis lineage.
- Citation-origin edges from reusable references back to the research records they cite.
- Expanded graph filters and relationship labels.

## Architecture
Schema-stable: storage 35, Project 20.0, Project Export 20.0, Notebook Workspace 8.0. The graph is derived at runtime and is not a duplicate database.

## Governance
No semantic embeddings, server graph database, hidden relationship inference, automatic AI, or automatic mutation.
