# Sustainable Catalyst Workspace v0.76.0
## Documentation, Recovery Guidance & Product Help

v0.76.0 makes Workspace easier to understand and safer to recover without changing the canonical project model.

### Product-help surface

Workspace adds **Start → Help & Recovery**, a searchable local help surface. It documents the product boundary at the moment users need it rather than sending them to an external manual for basic questions.

The initial topics cover:

1. first-project creation;
2. local-first storage;
3. explicit recovery backup;
4. restore-as-copy;
5. save-verification failures;
6. rejected imports and unsupported future schemas;
7. cross-device sync conflicts;
8. device migration;
9. shared-review reconciliation; and
10. institutional handoff.

### Recovery principle

Preserve evidence before attempting repair. If Workspace reports an integrity problem, the preferred order is:

1. preserve a portable or recovery copy when possible;
2. inspect Persistence Integrity and the available recovery candidates;
3. restore as a new local copy rather than silently replacing the source;
4. compare states before deleting anything; and
5. keep site/plugin runtime failures separate from browser-local project recovery.

### Local-first boundary

Guest projects remain browser-local. Signing in does not silently upload project content. Account recovery backup is separate from sync enrollment. Sync remains explicit and conflict-safe. Imports remain staged before commit.

### Governance

Product Help is advisory. It does not automatically repair state, restore a project, upload content, enroll a project in sync, reconcile reviewer input, perform an institutional transfer, invoke AI, or change lifecycle state.

The optional help-context report is privacy-minimized and contains only the selected help topic/category and the current help view. It excludes project content, project titles, source URLs, query text, device identifiers, and account identity.

### Schema boundary

- Storage: 35
- Project: `sc-workspace-project/20.0`
- Project Export: `sc-workspace-project-export/20.0`
- Canonical migration: none
