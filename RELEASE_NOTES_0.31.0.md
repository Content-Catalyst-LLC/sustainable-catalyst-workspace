# Sustainable Catalyst Workspace v0.31.0

## Public Beta Hardening & Field Diagnostics

v0.31.0 is a schema-stable hardening release focused on real-world public-beta operation before the Research Notebook series begins.

### Added

- Local Field Diagnostics in Storage & Identity.
- Browser capability, local-storage latency, workspace-size, parse/serialization latency, DOM-density, recovery, and deployment-profile checks.
- Explicit advisory thresholds with named attention signals and no hidden health score.
- User-generated JSON issue reports with issue type, impact, observed behavior, expected behavior, and reproduction steps.
- Portable text support summaries.
- `/wp-json/sc-workspace/v1/field-diagnostics-contract`.
- `sc-workspace-field-diagnostic/1.0` and `sc-workspace-field-report/1.0` schemas.
- A Start-screen route into Field Diagnostics for public-beta troubleshooting.

### Privacy and governance

Diagnostics remain local until the user exports them. Workspace does not automatically attach project content, object text, source URLs, local device identity, query strings, or page fragments. Reports are never submitted automatically, and no behavioral telemetry or hidden health/readiness score is introduced.

### Compatibility

Storage remains schema 27 and project schema remains `sc-workspace-project/12.0`; no project or Workspace-state migration is required.
