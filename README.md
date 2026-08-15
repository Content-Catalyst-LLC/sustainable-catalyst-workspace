# Sustainable Catalyst Workspace v0.82.1

## Production Certification Installer & Validation Lineage Repair

Sustainable Catalyst Workspace is a free, local-first environment for carrying questions, evidence, analysis, decisions, composition, review, and deliberate handoff across Sustainable Catalyst.

v0.82.1 is a surgical Release Candidate repair after the v0.82.0 installer stopped on an inherited Security & Privacy Audit II plugin-version mismatch. The release does not add a new product subsystem and does not change canonical project/storage formats.

The installer now verifies release lineage before rsync, immediately after rsync into the Git target, and again before commit/push. Inherited validators preserve their historical release contracts while deriving the currently installed WordPress/runtime/cumulative-asset version from the live source tree.

Canonical contracts remain frozen at Storage 35, Project `sc-workspace-project/20.0`, and Project Export `sc-workspace-project-export/20.0`.

See `RELEASE_NOTES_0.82.1.md`, `VALIDATION_REPORT_0.82.1.md`, and `docs/PRODUCTION_CERTIFICATION_INSTALLER_VALIDATION_LINEAGE_REPAIR_V0821.md`.
