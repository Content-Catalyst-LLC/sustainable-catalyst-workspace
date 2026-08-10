# Sustainable Catalyst Workspace v0.34.0 — Notebook Collections & Knowledge Linking

Release date: 2026-08-09

## Purpose

v0.34.0 turns Research Notebook from a capture-only working surface into an explicitly connected research environment. Notes, sources, excerpts, sections, notebooks, and existing Workspace objects can now be grouped into collections and connected with human-created relationships. Backlinks are derived from those explicit links rather than inferred by a model.

## What changed

- Adds project-bound Research Collections that can group notebooks, sections, individual notebook blocks, and existing Workspace objects without duplicating canonical object content.
- Adds explicit cross-notebook and notebook-to-object links with `references`, `supports`, `contrasts`, `extends`, and `related` relationships.
- Adds derived backlinks for linked notebook blocks and a project-level count of backlinked targets.
- Adds inspectable link and collection management directly in the Notebook view, including open-target and removal actions.
- Adds portable Notebook Export v3 context so exported notebooks carry relevant explicit links and collection membership alongside notebook content.
- Keeps Source Capture, bibliographic context, explicit promotion, local-first persistence, restore points, account backup, and explicit sync boundaries intact.
- Corrects the public Notebook and Project REST contracts so their advertised project/export/notebook schemas match the v0.34 runtime.
- Advances account backup/sync validation to accept Project v15 while retaining the supported v14/v13/v12/v11 migration window.
- Does not add semantic embeddings, inferred relationships, automatic AI, automatic citation generation, remote fetch, publication, or automatic upload.

## Migration

- Workspace storage: 29 → 30
- Project schema: `sc-workspace-project/14.0` → `sc-workspace-project/15.0`
- Project export: `sc-workspace-project-export/14.0` → `sc-workspace-project-export/15.0`
- Notebook workspace: `sc-workspace-notebook-workspace/2.0` → `3.0`
- Notebook: remains `sc-workspace-notebook/2.0`
- Notebook block: remains `sc-workspace-notebook-block/2.0`
- Notebook export: `sc-workspace-notebook-export/2.0` → `3.0`

Existing v0.33 notebooks, source captures, capture provenance, bibliographic context, object references, promotions, project IDs, lifecycle milestones, restore points, Safe Actions, reconciliation receipts, account recovery metadata, and sync enrollment are preserved. Collections and links initialize empty until the user creates them.

## Governance boundary

A link exists only because a user created it. A backlink exists only because an explicit stored link points to that item. Collections store references to material already in the project; they do not establish a second canonical object database. No hidden relevance score or semantic relationship inference is introduced.

## Roadmap handoff

v0.34.0 establishes the explicit knowledge-linking substrate needed by v0.35.0 Notebook-to-Workspace Intelligence and later v0.36.0 synthesis/citation workflows. Those later releases can rely on stable, inspectable research relationships rather than reconstructing them from prose.
