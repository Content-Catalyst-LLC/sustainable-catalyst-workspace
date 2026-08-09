# Sustainable Catalyst Workspace v0.11.0

## Templates & Guided Workflows

v0.11.0 adds an optional guided-method layer without turning Workspace into a rigid wizard. Six built-in templates expose a transparent sequence across Research, Analysis, Decision, Canvas, Traceability, and Briefing modes.

### Changes

- Adds **Guide** as a project mode.
- Adds Research Investigation, Evidence Review, Analytical Assessment, Decision Case, Systems Mapping, and Publication Preparation templates.
- Supports multiple guided workflow runs in one project.
- Makes step status and notes explicit and editable.
- Opens the relevant native Workspace mode from each workflow step.
- Preserves blank projects and existing modes.
- Never generates hidden findings, infers completion, or authorizes decisions.

### Data boundary

Storage advances to schema 12 and projects to `sc-workspace-project/10.0`. Existing v0.10.0 projects migrate non-destructively and receive an empty `sc-workspace-guided-workflows/1.0` container.
