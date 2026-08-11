# Sustainable Catalyst Workspace v0.63.0 — Cross-Browser & Device Compatibility

## Purpose
Harden Workspace across Chromium, Edge, Safari/WebKit, Firefox/Gecko, desktop operating systems, tablet-class environments, narrow viewports, touch/pointer input, and embedded WordPress contexts while preserving the v0.62 persistence and recovery boundary.

## Added
- Feature-detected Browser & Device Compatibility runtime adapter.
- File import fallback from `File.text()` to `FileReader.readAsText()`.
- Guarded client-side export path with Blob/object URL first and a bounded small-data URI fallback.
- Guarded History API writes with in-app-only fallback when browser history state cannot be used.
- Root-bound viewport/device adapter with ResizeObserver and resize-event fallback behavior.
- Compatibility review surface under Review → Compatibility.
- Privacy-minimized browser compatibility report export.
- Explicit compatibility target-matrix export for manual QA.
- REST contract: `/wp-json/sc-workspace/v1/compatibility-contract`.

## Compatibility policy
Runtime behavior is selected by capability detection. Browser-family/platform-family labels are for diagnostics only and do not gate research functionality.

Automated tests cover capability permutations and fallback behavior. They do not constitute manual certification of every physical browser/device combination; the exported target matrix remains the field-QA checklist.

## Schema / governance
No canonical schema migration. Storage remains **35**, Project remains **20.0**, Project Export remains **20.0**, and Notebook Workspace remains **8.0**. No telemetry, device fingerprinting, automatic upload, automatic repair, or hidden compatibility score was added.
