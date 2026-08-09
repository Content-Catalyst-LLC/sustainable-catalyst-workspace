# Sustainable Catalyst Workspace v0.20.0

## Stability, Accessibility & Release Readiness

This consolidation release hardens the public Workspace runtime without adding another major subsystem or migrating project data.

### Stability and recovery
- Adds a last-known-good browser-local snapshot before verified writes when a readable previous state exists.
- Adds read-after-write persistence verification.
- Falls back visibly to the last-known-good state after quarantining damaged saved state when recovery is possible.
- Adds an explicit emergency Workspace backup export; it contains project content but excludes the local pseudonymous device identifier.

### Release diagnostics
- Adds Local Health & Recovery to the Storage & Identity drawer.
- Checks local storage availability, serialization, recovery-snapshot availability, SHA-256/Web Crypto support, reduced-motion preference, online state, and approximate local Workspace size.
- Diagnostic exports are local and privacy-minimized: no project/object content, source URLs, or device identifier.
- No automatic telemetry or server diagnostics are introduced.

### Accessibility
- Adds an application skip link.
- Strengthens visible focus behavior and focus movement after top-level Workspace view changes.
- Adds `prefers-reduced-motion` and forced-colors support.
- Sets WCAG 2.2 AA as the release accessibility target.

### Data boundary
No storage or project migration occurs. Storage remains schema 20 and projects remain `sc-workspace-project/11.0`. Cloud sync and server project storage remain disabled.
