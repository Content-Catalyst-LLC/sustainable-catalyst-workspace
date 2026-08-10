# Sustainable Catalyst Workspace v0.36.0

## Notebook Synthesis & Citation Workspace

v0.36.0 turns explicitly selected notebook research and Workspace objects into reviewable synthesis outputs without replacing the underlying material.

### Added

- Five synthesis modes: Outline, Citation Pack, Source Matrix, Evidence Summary, and Research Synthesis Draft.
- Explicit multi-selection of notebook blocks and structured Workspace objects.
- Project-bound synthesis records with selected-reference provenance.
- Citation carrying from recorded bibliographic/provenance fields only; missing citation facts remain missing.
- Portable synthesis export containing the synthesis, selected material, and governance boundary.
- Optional materialization of a synthesis as a standard Workspace Document object.
- Visible count and synthesis history in the Research Notebook interface.
- Notebook Workspace v5, Notebook Export v5, Notebook Synthesis v1, Notebook Synthesis Export v1, Project v17, and Project Export v17 contracts.

### Preserved

- v0.35 notebook promotion ledger and all promoted derivatives.
- v0.34 collections, explicit links, and derived backlinks.
- v0.33 Source Capture and bibliographic context.
- Original notebook blocks and Workspace objects after synthesis.
- Local-first persistence, recovery, account backup, explicit sync, change review, reconciliation, and governance state.

### Governance

Synthesis requires explicit user selection. Workspace does not automatically choose material, infer evidentiary strength, fabricate missing citation data, generate hidden claims, require AI, fetch sources, or mutate the selected research.

### Migration

Storage schema advances from 31 to 32 and project schema from 16.0 to 17.0. Existing Notebook Workspace v4 state is upgraded to v5 with an empty synthesis collection while prior notebooks, links, collections, promotions, source capture, and project state are retained.
