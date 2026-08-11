# Sustainable Catalyst Workspace v0.64.0 — Accessibility & Keyboard-First Product Audit

## Purpose
Harden Workspace for keyboard-first operation, predictable focus, programmatic structure, reduced-motion preferences, forced-colors environments, zoom/reflow field testing, and screen-reader verification while preserving the v0.61–v0.63 reliability, persistence, and compatibility boundaries.

## Added
- `SCWorkspaceAccessibility` runtime layer.
- Review → Accessibility audit surface.
- Local privacy-minimized accessibility report export.
- Explicit manual WCAG 2.2 AA checklist export.
- Arrow-key/Home/End navigation inside marked Workspace navigation groups.
- Modal Tab containment and opener focus restoration.
- Escape-to-close behavior when a dialog exposes an explicit close/cancel control.
- Stronger visible-focus presentation.
- Reduced-motion and forced-colors presentation hardening.
- Touch-target hardening for touch-capable environments.
- REST contract: `/wp-json/sc-workspace/v1/accessibility-contract`.

## Corrected
- Normalized top-level section switching so every registered Workspace route uses the same visibility rule. This closes a route-isolation gap affecting newer Review/Exchange surfaces and ensures keyboard and pointer activation produce the same visible result.
- Command palette routing now includes the newer Review hardening surfaces, including Accessibility.

## Accessibility claim boundary
Workspace targets **WCAG 2.2 AA**. Automated DOM/runtime tests and local audit findings support remediation but do **not** establish conformance or accessibility certification. Screen-reader behavior, measured contrast, complete keyboard task flows, zoom/reflow, forced colors, and device-specific touch behavior remain manual release-gate checks.

## Schema / governance
No canonical schema migration. Storage remains **35**, Project remains **20.0**, Project Export remains **20.0**, and Notebook Workspace remains **8.0**. No telemetry, automatic submission, automatic canonical repair, hidden accessibility score, or device fingerprinting was added.
