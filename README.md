# Sustainable Catalyst Workspace

Current release: **v0.63.0 — Cross-Browser & Device Compatibility**

Workspace is the free, local-first Sustainable Catalyst research and decision environment. v0.63.0 hardens browser and device behavior through feature-detected compatibility adapters for imports, downloads, browser history, viewport sizing, touch/pointer contexts, and WordPress embedding. The release publishes a privacy-minimized compatibility report and an explicit manual-QA target matrix; automated probes do not claim physical browser/device certification.

Canonical public route: `/platform/`

Canonical Knowledge Library route: `/knowledge-libraries/`

Core data contracts remain schema-stable at Storage 35, Project 20.0, Project Export 20.0, and Notebook Workspace 8.0.

v0.62.0 persistence protections remain in force: verified-save integrity receipts, an interrupted-write journal, checksum-bound last-known-good snapshots, and non-destructive recovery candidates. FNV-1a remains a corruption/drift detector only—not encryption, authentication, or a security signature.
