# Sustainable Catalyst Workspace v0.19.0

## Institutional Handoff

v0.19.0 introduces a governed handoff boundary between the free personal Workspace and Catalyst Intelligence. Mature work can be prepared as an explicit institutional-copy package while the original Workspace project remains independent and device-local.

### Changes

- Adds a top-level **Institutional** Workspace view.
- Prepares selected canonical Workspace Objects for an explicit Catalyst Intelligence promotion package.
- Requires human acknowledgement of the copy model, receiving-system governance boundary, and sharing scope.
- Provides explainable readiness checks rather than a readiness score.
- Exports SHA-256 fingerprinted, privacy-minimized institutional promotion packages.
- Excludes device/account identity, connected-tool handoff state, recent-tool history, activity history, AI review history, and collaboration history from the promotion package.
- Imports institutional receipts only when handoff ID, source project ID, and target product match.
- Receipt imports update only handoff status/metadata; they do not mutate source project content.
- Adds Activity Intelligence signals for institutional handoffs awaiting receipt.

### Governance boundary

Workspace does not become an institutional tenant in this release. v0.19.0 does not add organization membership, server permissions, shared cloud storage, automatic institutional upload, automatic ingestion, or live institutional collaboration. Catalyst Intelligence must independently accept and govern any promoted copy.

### Data boundary

Storage advances from schema 19 to schema 20. Project schema remains `sc-workspace-project/11.0`; existing projects are not rewritten to support institutional handoff.
