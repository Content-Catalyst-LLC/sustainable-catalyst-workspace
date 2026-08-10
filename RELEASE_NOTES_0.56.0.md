# Sustainable Catalyst Workspace v0.56.0 — Research Automation Framework

v0.56.0 adds explicit, browser-local research routines without introducing background automation or canonical research mutation.

## Added
- User-authored routines for recurring import review, source review, verification checks, synthesis refresh proposals, and workflow actions.
- Declarative on-demand/daily/weekly/monthly cadence metadata.
- `Run now` and `Run due routines` as the only execution boundaries.
- Reviewable automation run receipts with findings and recommended explicit actions.
- Canonical Integrated Knowledge targets that remain visibly unresolved rather than silently rebinding.
- Portable integrity-fingerprinted automation library export/import.
- Review → Automation Workspace surface.
- `/wp-json/sc-workspace/v1/research-automation-contract`.

## Governance
Schedules do not execute in the background. Routines do not perform automatic network requests, imports, AI calls, task creation, verification state changes, synthesis replacement, or canonical mutation. Imported routines never execute automatically.

Storage 35, Project 20.0, Project Export 20.0, and Notebook Workspace 8.0 remain unchanged. The v0.55 API/embed privacy boundary and 4px editorial header rule are retained.
