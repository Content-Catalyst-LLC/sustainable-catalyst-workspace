# Sustainable Catalyst Workspace v0.14.0

## Import & Interoperability

v0.14.0 adds a local-first import and interchange boundary for moving structured work into and out of Workspace without silently overwriting canonical objects or elevating imported material to trusted evidence.

### Changes

- Adds a top-level **Import & Interoperability** Workspace view.
- Stages JSON, CSV/TSV, Markdown, HTML, and plain-text files locally before commit.
- Requires target-project selection and explicit human commit.
- Creates imported artifacts as draft canonical Workspace Objects with `imported` provenance.
- Calculates a SHA-256 fingerprint of the staged source file when Web Crypto is available.
- Imports CSV/TSV and generic JSON as Dataset objects; Markdown/HTML/text as Document objects.
- Accepts canonical Workspace object exports and v1 interchange packages.
- Never silently overwrites an existing object ID; imported objects receive new stable local IDs.
- Exports portable `sc-workspace-interchange/1.0` JSON packages with canonical objects and traceability lineage.
- Keeps parsing, staging, and commit operations in the browser; Workspace does not provide a server import pipeline.
- Imported material remains unverified until the user reviews it through the existing evidence/provenance workflow.

### Data boundary

Storage advances from schema 14 to 15 to add Workspace-level interoperability activity. Project schema remains `sc-workspace-project/11.0`; existing projects are not rewritten.
