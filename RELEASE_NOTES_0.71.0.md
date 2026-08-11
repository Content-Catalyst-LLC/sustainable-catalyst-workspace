# Sustainable Catalyst Workspace v0.71.0 — First-Run Onboarding & Project Creation

## Purpose

v0.71.0 improves the first five minutes of Workspace after Public Product Beta III. It gives a browser with no local Workspace projects a clear, explicit path into real work without adding a login wall, a new project model, or inferred setup behavior.

## First-run experience

A new **First Run / Your First Project** panel appears on Start only when the local project count is zero. The user can provide a project name, optionally describe the purpose, and choose one of five starting shapes:

1. Blank project
2. Research investigation
3. Analytical assessment
4. Decision case
5. Publication preparation

The standard project form remains available as an alternate path.

## Project-creation boundary

Project creation occurs only after the user submits **Create first project**. Merely selecting a starter does not create or modify a project. Blank projects reuse the canonical project template. Guided starters reuse the existing guided-workflow engine, so v0.71.0 does not introduce a parallel project representation.

Guided starts do not infer answers, complete steps, advance lifecycle state, upload content, enroll sync, or invoke AI automatically.

## Local-first orientation

The first-run surface states the persistence boundary at the moment a project is created. Guest use remains first-class. For a signed-in user, project creation still writes locally; account backup and cross-device sync remain separate explicit actions.

First-run status is derived from the local project count rather than a persistent behavioral profile.

## Accessibility and field use

The first-run form uses explicit labels, a fieldset/legend for starter selection, a live status region, bounded input widths, responsive two-column-to-single-column reflow, and 44 px phone-scale actions. It inherits the accessibility, compatibility, responsive, persistence, recovery, sync, and performance protections already present in Workspace.

## Schema stability

- Storage: `35`
- Project: `sc-workspace-project/20.0`
- Project Export: `sc-workspace-project-export/20.0`
- Schema migration: **not required**

All v0.62–v0.70 hardening and Public Product Beta III behavior remains in place.
