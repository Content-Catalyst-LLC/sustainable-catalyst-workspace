# Sustainable Catalyst Workspace v2.0.4 — Visual Regression, Theme Isolation & Cross-Viewport Hardening

## Purpose
Prevent WordPress/theme CSS and viewport-specific layout regressions from re-breaking the recovered v2 cockpit and connected-product controls.

## Changes
- Adds a rendered Chromium regression matrix at 1440, 1024, 768, and 390 px.
- Adds a hostile-theme fixture that forces ordinary buttons red and inline; Workspace components must remain correctly styled.
- Hardens `.scw-button` and Work Mode card presentation inside `.scw-shell.scw-root`.
- Adds horizontal-overflow guards and mobile wrapping for dense action groups.
- Preserves v2.0.3 root-scope recovery and every existing route/data contract.

## Boundaries
No routing change, no canonical content mutation, no migration, no automatic AI, and no telemetry.
