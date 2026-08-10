# v0.49.0 — Research Templates & Reusable Workflows

Workspace adds a second-generation reusable research protocol layer on top of the original v0.11 guided workflows.

## Built-in protocols

- Research Protocol
- Literature Review
- Evidence Review Protocol
- Decision Workflow
- Systems Inquiry
- Publication Workflow
- Rapid Research Assessment
- Source Validation Protocol

## Reusable structure

A template may define a guided-workflow scaffold, Notebook section names, a project-starter title/description, and optional empty starter-object definitions. Applying a template is always an explicit user action.

Custom templates may be captured from an active guided workflow. Capture strips project notes, step notes, object references, Notebook block contents, evidence, citations, findings, and completion status. Only reusable structure is retained.

## Persistence boundary

The custom template library is browser-local and portable through an integrity-fingerprinted JSON package. Built-in templates are immutable. Project 20.0, Project Export 20.0, Storage 35, and Notebook Workspace 8.0 remain unchanged.

## Governance

Templates do not run automatically, mark steps complete, generate findings, invoke AI, or mutate canonical research until the user explicitly chooses Apply or Create project starter. Blank projects remain first-class.
