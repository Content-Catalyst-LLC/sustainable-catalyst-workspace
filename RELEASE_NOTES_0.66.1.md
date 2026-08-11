# Sustainable Catalyst Workspace v0.66.1 — WordPress Plugin Header Metadata Recovery

v0.66.1 is a surgical packaging/runtime-metadata hotfix over v0.66.0.

## Fixed

- Required WordPress plugin headers are now placed at the top of the main plugin file, safely inside WordPress's 8 KB plugin-header parsing window.
- The accumulated long-form Description header was replaced with a concise plugin description.
- `Version`, `Author`, `Requires at least`, `Requires PHP`, and `Text Domain` are now available within the first few hundred bytes of the main plugin file.
- Product Registry recovery lineage advances to v0.66.1 while retaining v0.66.0 as the predecessor.
- Public Beta II and import/export compatibility diagnostics report v0.66.1 as the running release.
- Added Python and PHP regression tests that emulate WordPress's bounded plugin-header read.

## Unchanged

- Storage schema: 35
- Project schema: `sc-workspace-project/20.0`
- Project export schema: `sc-workspace-project-export/20.0`
- v0.66 import/export and backward-compatibility behavior
- v0.65 responsive/field-use behavior
- v0.64.1 desktop-layout and WordPress dependency recovery

No canonical data migration is required.
