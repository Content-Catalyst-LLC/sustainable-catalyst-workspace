# Sustainable Catalyst Workspace v0.63.0 — Validation Report

Release: **v0.63.0 — Cross-Browser & Device Compatibility**
Predecessor: **v0.62.0**
Release date: **2026-08-10 (America/Chicago)**

## Release gate

**PASS**

## Automated validation

- Python contract suite: **799 tests passed**.
- JavaScript runtime suite: **44 runtime files passed**.
- PHP runtime suite: **5 runtime files passed**.
- Repository JavaScript syntax sweep: **119 files passed**.
- Repository PHP syntax sweep: **9 files passed**.
- JSON parse sweep: **339 JSON files passed**.
- `scripts/validate_release.py`: **PASS**.
- Release-diff whitespace check against v0.62.0: **PASS**.

## v0.63.0 compatibility checks

Validated:

- Storage schema remains **35**.
- Project schema remains **sc-workspace-project/20.0**.
- Project Export remains **20.0** and Notebook Workspace remains **8.0**.
- No canonical project/storage migration is introduced.
- Runtime decisions are feature-detected; browser-family labels are diagnostic only and do not gate Workspace functionality.
- Browser-local and session storage are probed defensively, including environments where direct storage-property access is blocked.
- Text-file import prefers `File.text()` and falls back to `FileReader.readAsText()`.
- The primary application import paths use the compatibility file reader.
- Shared review, institutional packages, research automation, and security/privacy verification also use the compatibility reader when available.
- Client-side exports prefer Blob/object URLs and support a bounded data-URI fallback for small payloads.
- Primary and secondary export surfaces route through the compatibility adapter when available.
- Browser History API writes are guarded and fall back to in-app-only navigation when state writes fail or are unavailable.
- Viewport sizing is root-bound for embedded WordPress contexts and reacts through `ResizeObserver` with window-event fallback behavior.
- Touch/pointer and embedded-context signals change presentation behavior without changing canonical research data.
- A dedicated **Review → Compatibility** surface exposes local capability findings.
- Compatibility report export omits the raw user-agent string, project/object content, source URLs, query strings, page fragments, and device identifiers.
- No compatibility telemetry, automatic submission, hidden device fingerprint, automatic repair, or canonical mutation is introduced.
- v0.62.0 persistence transaction, integrity receipt, and last-known-good protections remain intact.
- v0.62.0 release-manifest and product-record history are retained.

## Manual QA boundary

The automated runtime fixtures validate capability permutations and fallback behavior. They **do not certify every physical browser/device combination**. The v0.63 target matrix explicitly retains manual QA for Chrome/Chromium, Edge, Safari/WebKit, Firefox/Gecko, macOS, Windows, tablet-class iPadOS/iOS and Android environments, and compact/narrow viewport behavior.

## Result

**v0.63.0 passes the repository release gate and is ready for deployment and cross-browser/device field validation.**
