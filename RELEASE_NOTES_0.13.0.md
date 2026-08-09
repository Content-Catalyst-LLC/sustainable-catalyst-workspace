# Sustainable Catalyst Workspace v0.13.0

## Responsible AI Assistance

v0.13.0 adds an explicit, grounded AI-assistance boundary to Workspace. Users select the Workspace Objects that form the basis of an assistance request, prepare or export a grounded request locally, review any AI response as a draft, and explicitly accept or reject it. Workspace does not automatically send project content to a model, treat AI output as evidence, approve decisions, or publish responses.

### Changes

- Adds the **Assist** project mode.
- Adds six transparent task types for summaries, evidence gaps, comparisons, briefing drafts, method explanations, and grounded questions.
- Stores AI sessions locally inside the project.
- Makes selected grounding objects and provenance visible before use.
- Exports grounded request JSON and response JSON packages.
- Supports an explicit same-origin Research Librarian handoff through `sc_workspace_ai_request_v1`.
- Ships `sc-workspace-ai-adapter-v1.js` for compatible same-origin tools to read an explicitly prepared request and return a structured response.
- Accepts adapter responses through `sc_workspace_ai_response_v1` or same-origin `postMessage`, with local project/request matching and citation filtering against the original grounding set.
- Requires explicit human acceptance before AI output is materialized as a canonical Document object.
- Marks accepted documents `ai-assisted` and `human-accepted`.
- Records `derived-from` lineage to citation objects chosen during review.
- Keeps canonical Sources, Evidence, Analyses, Decisions, and other objects unchanged.

### Data boundary

Storage advances from schema 13 to 14 and projects from `sc-workspace-project/10.0` to `sc-workspace-project/11.0`. Existing projects migrate non-destructively and receive an empty `sc-workspace-ai-assistance/1.0` container. Personal Knowledge remains device-local.
