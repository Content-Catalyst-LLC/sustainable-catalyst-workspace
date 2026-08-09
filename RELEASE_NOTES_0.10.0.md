# Sustainable Catalyst Workspace v0.10.0

## Briefing & Publication Studio

v0.10.0 adds a native communication layer that turns connected project work into structured briefings, memos, reports, articles, and publication drafts without turning Workspace into a CMS.

### Changes

- Adds a Briefing project mode and `sc-workspace-briefing/1.0`.
- Supports five draft formats: briefing, memo, report, article, and publication draft.
- Adds deterministic format-specific outline templates; no AI text generation is required.
- Lets each draft reference existing Workspace Objects as its evidence/analysis/decision basis.
- Supports editable, reorderable sections.
- Materializes an active draft as a canonical `Document` Workspace Object.
- Exports Markdown, standalone HTML, and `sc-workspace-publication-export/1.0` JSON packages.
- Publication packages include traceable object metadata rather than silently copying every underlying object body.
- Does not automatically publish or write to WordPress, Publications, or the Knowledge Library.
- Retains `/knowledge-libraries/` as the canonical Knowledge Library route.

### Data boundary

Storage advances from schema 10 to 11 and project records from `sc-workspace-project/8.0` to `sc-workspace-project/9.0`. Existing project content is normalized non-destructively and receives an empty Briefing & Publication Studio workspace.
