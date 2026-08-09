# v0.11.0 — Templates & Guided Workflows

Workspace adds an optional method layer for projects that benefit from a visible sequence. Blank projects remain first-class.

## Built-in templates

- Research Investigation
- Evidence Review
- Analytical Assessment
- Decision Case
- Systems Mapping
- Publication Preparation

## Boundary

A template creates only a visible workflow run and step scaffold. It does not generate findings, mark work complete, create approvals, or hide method decisions. Users control step status and can open the relevant Workspace mode from each step.

## Persistence

Guided workflows are stored with the local project under `sc-workspace-guided-workflows/1.0`. Storage advances to schema 12; projects advance to `sc-workspace-project/10.0`.
