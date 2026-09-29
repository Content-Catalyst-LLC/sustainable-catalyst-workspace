# Workspace v3.35.0.1 — Installer Context Repair

This is a release-engineering repair for Workspace v3.35.0. The product version remains **3.35.0**.

## Why it exists

The original v3.35.0 installer used a unified Git patch generated from a simulated v3.34 baseline. On the user's real repository, `backend/app/main.py` and `backend/app/polyglot.py` had equivalent v3.34 functionality but different surrounding text/lineage, so exact patch application and Git three-way application failed. Git partially applied several other files before stopping.

## Repair behavior

The repaired installer no longer relies on patch context for the seven files intentionally modified by v3.35.0. Instead it:

1. accepts only v3.34.0 or partially-applied v3.35.0 baseline markers;
2. backs up all seven modified files under `.workspace-repair-backups/v3.35.0.1/<timestamp>/`;
3. overwrites exactly those seven files with the certified v3.35.0 versions;
4. installs the four new v3.35.0 payload files;
5. continues through the normal v3.35 validator, GNN regression tests, packaging, commit, push, and tag flow.

No repository reset is required. No database migration is introduced.
