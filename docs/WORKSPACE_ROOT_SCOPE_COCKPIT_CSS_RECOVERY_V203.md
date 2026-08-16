# Workspace v2.0.3 — Workspace Root Scope & Cockpit CSS Recovery

## Problem
The live Workspace application rendered its root wrapper as `scw-shell`, while a large mature portion of the cumulative stylesheet was intentionally scoped beneath `.scw-root`. As a result, those selectors could not match the live DOM. Global/theme button styles then won for Work Mode controls, producing the red strip/button appearance seen in production.

## Repair
The live root now renders as `class="scw-shell scw-root"`. The v2.0.3 cumulative stylesheet retains the mature `.scw-root …` descendant model and adds a small compound-selector safeguard for the cockpit. No global selector replacement is performed.

## Regression boundary
The release verifies that the live root contains both classes, that cockpit/work-mode selectors can match the DOM, and—during release certification—that Chromium computes the cockpit and Work Mode containers as grids and disabled cards as neutral rather than theme-red controls.

## Data and governance
Storage remains 35. Project remains `sc-workspace-project/20.0`. Export remains `sc-workspace-project-export/20.0`. No route semantics, canonical project content, AI behavior, telemetry, or migration behavior changes.
