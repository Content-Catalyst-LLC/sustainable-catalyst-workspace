# Sustainable Catalyst Workspace v1.1.0 — Workspace Home, Project Cockpit & Navigation Refinement

## Purpose
Move the post-GA product line back to visible usability improvement without changing Workspace's canonical data model.

## Changes
- Renames the primary `Start` area to **Home** while preserving the existing `start` view identifier for backward compatibility.
- Adds a **Project Cockpit** that summarizes the active project, local project/object/research/notebook counts, and explicit work-mode shortcuts.
- Adds deterministic next-action guidance derived only from visible local project state; no scoring, behavioral inference, telemetry, or automatic AI.
- Preserves first-run project creation for empty local workspaces and recent-project resume behavior for established workspaces.
- Reduces Review navigation density by keeping the most common routes visible and moving historical/release/diagnostic surfaces under progressive disclosure.
- Preserves command palette access, all specialized Workspace surfaces, Lab/Library/tool handoffs, local-first persistence, and explicit account/sync boundaries.

## Compatibility
Storage schema remains 35. Project schema remains `sc-workspace-project/20.0`. Export schema remains `sc-workspace-project-export/20.0`. No migration is required.
