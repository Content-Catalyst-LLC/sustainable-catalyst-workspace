# Sustainable Catalyst Workspace v0.15.0

## Share & Portable Projects

This release adds deliberate whole-project portability while preserving Workspace's local-first boundary. Users can create integrity-manifested portable project packages, export static HTML review copies, and import a package as a new local copy.

### Changes

- Adds a top-level **Share** Workspace view.
- Adds `sc-workspace-share/1.0` and `sc-workspace-portable-project/1.0`.
- Exports privacy-minimized whole-project JSON packages with SHA-256 integrity fingerprints when Web Crypto is available.
- Excludes device identity, persistence metadata, handoff/session state, recent-tool history, and account identity from portable packages.
- Makes project activity and Responsible AI review history explicit opt-in sharing choices.
- Exports a standalone static HTML review copy.
- Verifies portable-package integrity before import when a fingerprint is present.
- Imports portable projects as a **new local copy** with a new project ID and device-local persistence boundary.
- Never overwrites an existing local project automatically.
- Adds device-local sharing history.
- Adds `/wp-json/sc-workspace/v1/share-contract`.

### Data boundary

Storage advances from schema 15 to 16. Project schema remains `sc-workspace-project/11.0`; existing projects are not rewritten merely to support sharing. No cloud sync, public share links, server project upload, or live collaboration is added.
