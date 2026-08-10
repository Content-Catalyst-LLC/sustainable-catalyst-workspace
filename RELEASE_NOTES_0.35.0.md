# Sustainable Catalyst Workspace v0.35.0

## Notebook-to-Workspace Intelligence

v0.35.0 adds deliberate promotion of Research Notebook material into the structured Workspace environment.

### Added

- Explicit promotion destinations: Source, Evidence, Dataset, Analysis, Decision, Document, and Canvas.
- Project-bound notebook promotion ledger with source and target lineage.
- Multiple derivatives from the same notebook block.
- Visible promotion history in the Notebook interface.
- Canvas-node promotion using the existing Canvas model.
- Source promotion integration with the Research reading queue.
- Evidence promotion integration with existing Source/Evidence relationships when source context is available.
- Notebook Workspace v4, Notebook v3, Block v3, Notebook Export v4, and Promotion v1 schemas.
- Project schema v16 / Project Export v16.

### Preserved

- Original notebook material after promotion.
- v0.34 collections, explicit links, and derived backlinks.
- v0.33 Source Capture provenance and bibliographic context.
- Local-first project persistence and recovery boundaries.
- Account backup, explicit sync, version history, change review, reconciliation, and governance state.

### Governance

Promotion requires an explicit destination and user action. Workspace does not automatically promote, secretly classify, require AI, infer semantic links, fetch sources, upload notebook material, or overwrite source blocks.

### Migration

Storage schema advances from 30 to 31 and project schema from 15.0 to 16.0. The migration initializes the promotion ledger while preserving prior notebook and project state.
