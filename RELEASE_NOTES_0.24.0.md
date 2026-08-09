# Sustainable Catalyst Workspace v0.24.0

## Project Diff & Change Review

v0.24.0 adds deterministic project-state comparison on top of v0.23.0 restore points. Users can compare a restore point with the current project or another restore point from the same project before restoring, syncing, sharing, or promoting work.

### Changes

- Adds a top-level **Changes** environment.
- Compares canonical objects, research questions/claims, evidence links and assessments, analysis assumptions/methods/findings, decisions/options/criteria/assessments/risks, traceability relationships, reproducibility records, Canvas boards/nodes/edges, briefing drafts, and guided workflows.
- Reports explicit **Added / Removed / Modified** records and the fields changed on modified records.
- Surfaces transparent attention labels such as **Evidence basis changed**, **Assumptions changed**, **Decision record changed**, and **Relationships changed**.
- Exports portable `sc-workspace-change-review/1.0` JSON.
- Adds **Review changes** directly to restore-point cards.
- Makes no automatic merge, restore, sync, share, or institutional-promotion decision.
- Keeps Workspace storage schema **23** and project schema `sc-workspace-project/11.0` unchanged.

### Regression repair

The v0.23 normalization repair that preserves account-persistence and cross-device-sync metadata remains covered by the regression suite.
