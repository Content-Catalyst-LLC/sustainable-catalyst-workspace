# Sustainable Catalyst Workspace

Current release: **v0.62.0 — Product Hardening II: Persistence, Corruption & Recovery Integrity**

Workspace is the free, local-first Sustainable Catalyst research and decision environment. v0.62.0 hardens browser-local persistence with verified-save integrity receipts, a lightweight write transaction journal, interrupted-write detection, checksum-bound last-known-good snapshots, and explicit recovery candidate exports.

Canonical public route: `/platform/`

Canonical Knowledge Library route: `/knowledge-libraries/`

Core data contracts remain schema-stable at Storage 35, Project 20.0, Project Export 20.0, and Notebook Workspace 8.0.

Persistence safeguards preserve the local-first boundary. The FNV-1a receipt is a corruption/drift detector only—not encryption, authentication, or a security signature. v0.62 does not automatically repair, overwrite, restore, upload, or delete canonical research.
