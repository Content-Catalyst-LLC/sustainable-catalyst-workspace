# Sustainable Catalyst Workspace v0.8.1 — Cross-Product Return Adapters

Released: 2026-08-08

- Added `sc-workspace-return-adapter/1.0` producer/consumer compatibility layer.
- Added public producer helper `sc-workspace-return-adapter-v1.js` for Sustainable Catalyst tools.
- Added same-origin `postMessage` returns in addition to session-storage and portable JSON returns.
- Added tool-name alias normalization for all nine supported Workspace destinations.
- Automatic returns now require matching local project, handoff ID, and destination.
- Added browser-session duplicate-return receipts when producers provide a `returnId`.
- Manual return JSON import remains available for explicit recovery and interoperability.
- Added `/wp-json/sc-workspace/v1/adapter-contract`.
- No Workspace storage/project/object schema change; existing v0.8.0 project data is untouched.
- Guest access, free public use, device-local persistence, and the no-cloud/no-server-broker boundary remain unchanged.
