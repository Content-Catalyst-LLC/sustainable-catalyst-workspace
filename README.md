# Sustainable Catalyst Workspace

Current release: **v0.66.1 — WordPress Plugin Header Metadata Recovery**

Workspace is the free, local-first Sustainable Catalyst research and decision environment. v0.66.1 is a surgical WordPress packaging hotfix over v0.66.0: required plugin metadata now stays inside WordPress’s 8 KB header parsing window while all v0.66 import/export hardening remains unchanged.

Canonical public route: `/platform/`

Canonical Knowledge Library route: `/knowledge-libraries/`

Core data contracts remain schema-stable at Storage 35, Project 20.0, Project Export 20.0, and Notebook Workspace 8.0. v0.66.1 does not migrate canonical Workspace data.

Project Import recognizes the documented Workspace Project and Project Export schema generations from 1.0 through 20.0, including 3.1. Selecting a file never commits it automatically. Supported legacy material is normalized only after explicit import commit and is always assigned a new local project ID; future project schemas are blocked rather than silently downgraded.

Project Export now performs a current-schema round-trip projection check before writing the file. The FNV-1a fingerprint used by that check is a deterministic drift detector only—not encryption, authentication, or a security signature.

v0.65.0 responsive/field-use behavior and contextual Lab handoffs remain in force. v0.64.1 accessibility runtime/dependency protection, v0.63 browser compatibility fallbacks, and v0.62 persistence/recovery protections remain retained.
