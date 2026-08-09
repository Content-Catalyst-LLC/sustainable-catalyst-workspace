# v0.20.0 — Stability, Accessibility & Release Readiness

v0.20.0 is a consolidation release for the public Sustainable Catalyst Workspace. It deliberately adds no new project subsystem and requires no storage or project schema migration.

## Stability

- Preserve a last-known-good local snapshot before verified writes when a readable prior state exists.
- Verify browser-local saves with a read-after-write comparison.
- Quarantine damaged current state and visibly fall back to the last-known-good snapshot when one is available.
- Keep existing recovery isolation behavior when no usable fallback exists.
- Provide an explicit emergency Workspace backup export containing project content but excluding the local pseudonymous device identifier.

## Local diagnostics

The Storage & Identity drawer now includes a Local Health & Recovery surface. Diagnostics stay entirely in the browser and report only capability/status information: storage availability, state serialization, recovery-snapshot availability, Web Crypto/SHA-256 support, reduced-motion preference, online state, project/object counts, and approximate serialized Workspace size.

Diagnostic exports do not include project content, object content, source URLs, or the local device identifier. Workspace does not transmit diagnostics or add telemetry in this release.

## Accessibility

v0.20.0 adds an explicit WCAG 2.2 AA target and strengthens the application shell with a skip link, visible focus treatment, focus movement after top-level Workspace view changes, `prefers-reduced-motion` handling, and `forced-colors` resilience. Existing keyboard-operable graph nodes and live save/recovery messaging remain part of the accessible contract.

## Data boundary

- Storage schema: `20` → `20`
- Project schema: `sc-workspace-project/11.0` → `sc-workspace-project/11.0`
- Cloud sync: disabled
- Server project storage: disabled
- Automatic telemetry: disabled
- Canonical public route: `/platform/`
- Canonical Knowledge Library route: `/knowledge-libraries/`
