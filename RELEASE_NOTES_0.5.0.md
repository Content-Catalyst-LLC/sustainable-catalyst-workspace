# Sustainable Catalyst Workspace v0.5.0
## Analysis Workspace

Released 2026-08-08.

### Added
- First-class Analysis Workspace inside every active Workspace Project.
- `sc-workspace-analysis/1.0` project sub-contract.
- Analysis questions with priority, status, and active-question state.
- Dataset registration that creates canonical `Dataset` Workspace Objects.
- Variable registry with outcome, input, control, parameter, and indicator roles.
- Assumption registry with untested, supported, and challenged states.
- Method registry covering descriptive, comparative, statistical, modeling, scenario, sensitivity, and other methods.
- Method creation also creates a canonical `Analysis` Workspace Object and can reference Dataset object IDs.
- Structured comparisons with baseline, alternative, metric, result, and interpretation.
- Findings with preliminary, supported, and contested states plus Evidence-object references.
- Analysis launchers for Analytics R, Workbench, Catalyst Data, and Site Intelligence.
- `/wp-json/sc-workspace/v1/analysis-contract`.
- Project schema `sc-workspace-project/4.0`, export schema `sc-workspace-project-export/4.0`, handoff schema `sc-workspace-handoff/1.3`, and storage schema 6.

### Migration
v0.4.1 projects migrate in place. Existing projects, notes, Research Workspace state, Workspace Objects, provenance, device-local persistence metadata, and stable object IDs are retained. Each migrated project receives an empty normalized Analysis Workspace.

### Persistence and business-model boundary
Workspace remains free, guest-accessible, account-aware, and device-local. v0.5.0 does not introduce server compute, automatic cloud upload, collaboration, team governance, or organization-scale intelligence. Those boundaries remain available for future hosted Workspace capabilities and the Catalyst Intelligence institutional layer.
