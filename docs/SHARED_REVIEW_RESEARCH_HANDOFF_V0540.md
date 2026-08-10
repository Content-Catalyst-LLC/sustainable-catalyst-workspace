# v0.54.0 — Shared Review & Research Handoff

Workspace now bridges the v0.53 Collaboration Architecture and the earlier portable-review capability with a controlled research-handoff workflow.

## Capabilities
- Create a handoff against one canonical Workspace Project with an explicit set of active object IDs.
- Assign declared reviewers from the project's collaboration policy.
- Prepare a frozen review package containing only the selected object snapshots plus relevant collaboration comments/proposals and ownership context.
- Fingerprint the frozen package so later project edits do not silently rewrite the material that was actually reviewed.
- Export the review package explicitly; Workspace never sends it automatically.
- A reviewer can import the package, choose a declared reviewer identity, record a review decision, and export a fingerprint-bound response.
- Source Workspace import requires the response to match the original package/handoff/project fingerprint.
- Responses are staged before commit.
- Explicit commit merges imported comments and submitted proposals into the v0.53 Collaboration Architecture ledger.
- Imported review responses never directly mutate canonical project objects; accepted proposals remain review decisions only.
- Missing projects remain unresolved rather than being silently rebound.

## Governance boundary
This is asynchronous shared review and research handoff, not live co-editing or a shared tenant. Review packages are deliberate portable copies of an explicit research scope. There is no automatic external transmission, organization membership, server-side collaboration, automatic proposal application, or background canonical mutation.

## Schema boundary
Storage remains 35 and Project remains `sc-workspace-project/20.0`. Shared Review uses a browser-local ledger and portable package/response schemas, so no project migration is required.
