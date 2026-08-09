# Sustainable Catalyst Workspace v0.17.0

## Workflow & Activity Intelligence

v0.17.0 adds a transparent, device-local activity layer across Workspace projects. It summarizes explicit project activity, guided-workflow status, unresolved review conditions, connected-tool handoffs, and user-created next actions without creating a productivity score or server telemetry stream.

### Changes

- Adds a top-level **Activity** Workspace view.
- Adds user-controlled next actions with project, priority, optional due date, and explicit status.
- Derives explainable attention signals from visible project state.
- Surfaces active guided-workflow progress and the next incomplete step.
- Builds a cross-project local activity timeline from existing project activity records.
- Supports project, time-window, stale-threshold, and signal-kind filters.
- Supports dismiss/restore for derived attention signals.
- Adds `/wp-json/sc-workspace/v1/activity-intelligence-contract`.
- Advances workspace storage schema from 17 to 18 while keeping project schema `sc-workspace-project/11.0`.

### Governance boundary

- No productivity score.
- No time-on-page measurement.
- No behavioral telemetry.
- No server activity analytics.
- No automatic task or workflow completion.
- Derived signals are local, deterministic, and state the condition that produced them.
