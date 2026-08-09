# Sustainable Catalyst Workspace v0.32.0

## Research Notebook Foundation

v0.32.0 introduces a project-bound Research Notebook as the low-friction working surface between reading and structured Workspace artifacts.

### Added

- Multiple notebooks per Workspace Project.
- Reorderable notebook sections.
- Reorderable blocks for Note, Source, Excerpt, Question, Claim, Reference, Checklist, Divider, and Attachment Reference.
- Tags, source URLs, canonical object references, and promotion state on notebook blocks.
- Explicit promotion from notebook blocks into existing Workspace structures:
  - Source / Attachment Reference → Source object
  - Excerpt → Evidence object
  - Note / Checklist → Document object
  - Question → Research Question
  - Claim → Research Claim
- “Add to Notebook” action from the canonical object editor.
- Portable notebook JSON export using `sc-workspace-notebook-export/1.0`.
- Public `/wp-json/sc-workspace/v1/notebook-contract` contract.
- Dedicated notebook helper and JSON schemas.

### Data migration

- Workspace storage: `27 → 28`.
- Project schema: `sc-workspace-project/12.0 → sc-workspace-project/13.0`.
- Project export: `sc-workspace-project-export/12.0 → sc-workspace-project-export/13.0`.
- Existing projects receive an empty notebook workspace non-destructively.
- Existing canonical objects, research, analysis, decisions, lifecycle history, account persistence, sync metadata, restore points, Safe Actions, reconciliation receipts, collaboration, and institutional handoffs are preserved.

### Governance boundary

- Notebook is working memory, not a second authoritative object store.
- Promotions require an explicit human action and preserve the original notebook block.
- No AI runs automatically against notebook material.
- AI is not required to use Notebook.
- No automatic cloud upload or background synchronization is introduced.
- Account backup, explicit sync, restore points, and portable project copies inherit Notebook because it is part of the project boundary.
- Notebook-specific selective reconciliation/change review remains outside this foundation release and is planned for the later Notebook governance phase.

### Limits

- 30 notebooks per project.
- 40 sections per notebook.
- 300 blocks per notebook.
- 600 notebook blocks per project.

### Compatibility

The canonical Knowledge Library path remains `/knowledge-libraries/` and the public product remains available without an account.
