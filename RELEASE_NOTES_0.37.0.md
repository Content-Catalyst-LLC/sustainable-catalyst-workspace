# Sustainable Catalyst Workspace v0.37.0

## Grounded Notebook Assistance

v0.37.0 adds question-and-answer assistance over material the user explicitly selects from Research Notebook and existing Workspace objects. Answers are accepted only when their citation markers resolve to that selected grounding set, and returned assistance remains a reviewable draft.

### Added

- Grounded questions over explicitly selected notebook blocks and structured Workspace objects.
- Numbered grounding packets with stable references and recorded source/citation context.
- Citation-required response validation using `[1]`, `[2]`, and equivalent numbered markers bound to the selected set.
- Rejection of responses with no citations or citations outside the selected material.
- Provider-neutral request and response export contracts.
- A Notebook Assistance adapter for same-origin return workflows.
- Manual prompt copy/paste workflow when no compatible assistance provider is connected.
- Visible assistance history, status, selected materials, citations, response drafts, and review controls.
- Explicit optional materialization of an accepted assistance draft into a standard Workspace Document.
- Notebook Workspace v6, Notebook Export v6, Notebook Assistance v1, Assistance Request Export v1, Assistance Response Export v1, Project v18, and Project Export v18 contracts.

### Preserved

- v0.36 synthesis records and citation/source-selection lineage.
- v0.35 promotion ledger and promoted derivatives.
- v0.34 collections, explicit knowledge links, and derived backlinks.
- v0.33 Source Capture provenance and bibliographic context.
- Original notebook blocks and Workspace objects after assistance.
- Local-first persistence, recovery, optional account backup/sync, change review, reconciliation, and governance state.

### Governance

Workspace does not automatically select grounding material, submit a question to an AI provider, accept an answer, infer missing citations, permit citations outside the selected grounding set, mutate source material, create canonical evidence from an assistant answer, or automatically materialize a Document. Assistance output remains a draft until a user reviews and acts on it.

### Migration

Storage schema advances from 32 to 33 and project schema from 17.0 to 18.0. Existing Notebook Workspace v5 state is upgraded to v6 with an empty assistance collection while synthesis records, promotions, collections, links, source capture, notebooks, and project state are retained.
