# Grounded Research Assistant II — v0.51.0

Grounded Research Assistant II extends the explicit-selection, citation-required model introduced for Research Notebooks across the Integrated Knowledge Workspace.

## Boundaries

- Scope is selected explicitly from canonical Integrated Knowledge results.
- Request packets freeze a bounded snapshot of the selected grounding set with deterministic fingerprints.
- Workspace does not invoke an AI provider automatically.
- Responses must use valid `[n]` markers that resolve to the frozen grounding set.
- Every substantive response segment must contain a valid grounding citation.
- Invalid or out-of-scope citation markers are rejected.
- Accepted responses remain reviewable drafts.
- Canonical Document creation is an explicit user action.
- No metadata invention, semantic scope expansion, or automatic canonical mutation occurs.

Storage 35, Project 20.0, Project Export 20.0, and Notebook Workspace 8.0 remain unchanged.
