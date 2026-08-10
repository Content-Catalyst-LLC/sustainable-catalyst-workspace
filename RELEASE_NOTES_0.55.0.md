# Sustainable Catalyst Workspace v0.55.0 — Workspace API & Embed Foundation

v0.55.0 establishes a stable read-only integration boundary over the schema-stable Workspace architecture.

## Added

- Durable `scw://project/{project}/{kind}/{id}` references for Integrated Knowledge records.
- Explicit browser-local public-readonly projections.
- Selective disclosure of summary, tags, recorded provenance, and full content.
- Static read-only JSON API envelopes.
- Self-contained read-only embed descriptors and renderer.
- Public renderer helper URL for compatible sites.
- Exchange → API & Embed interface.
- Public `/wp-json/sc-workspace/v1/api-embed-contract` metadata contract.

## Privacy and security boundary

Canonical Workspace research remains private/browser-local by default. The public REST contract does not enumerate projects or return user research. A durable reference is an identifier only and never an authorization token. Static projection fingerprints are integrity receipts, not signatures or credentials.

No live server project API, server project discovery, automatic publication, background refresh, or canonical mutation is introduced.

## Compatibility

Storage remains 35, Project remains `sc-workspace-project/20.0`, Project Export remains 20.0, and Notebook Workspace remains 8.0. The v0.54 Shared Review & Research Handoff release remains intact as the immediate predecessor. The 4px editorial header rule is retained.
