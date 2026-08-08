# Sustainable Catalyst Workspace v0.8.0 — Cross-Product Handoffs

## Purpose
v0.8.0 makes Workspace the common personal context layer across Sustainable Catalyst tools. A tool launch is no longer just a URL jump: it creates a durable project handoff record with a stable handoff ID, destination, intent, object references, and return state.

## Boundary
- Workspace remains usable without an account.
- Projects and project content remain browser-local.
- Outbound URLs contain stable IDs and non-sensitive intent only.
- No titles, notes, object content, evidence text, dataset contents, decision rationale, or Canvas node content are serialized into handoff query strings.
- No server-side handoff broker is introduced.

## Contracts
- `sc-workspace-handoff/2.0` — outbound ephemeral session envelope.
- `sc-workspace-handoff-ledger/1.0` — durable per-project local ledger.
- `sc-workspace-handoff-return/1.0` — structured return package.
- Project schema advances to `sc-workspace-project/7.0`; storage schema advances to 9.

## Return paths
Compatible same-origin Sustainable Catalyst tools may place a `sc-workspace-handoff-return/1.0` packet in the documented sessionStorage return key before navigating back to Workspace. A portable JSON return package can also be imported manually. Returned artifacts are normalized into canonical Workspace Objects with `tool` provenance.

## Destinations
Research Librarian, Knowledge Library, Site Intelligence, Workbench, Analytics R, Decision Studio, Catalyst Canvas, Catalyst Data, and Lab.

## Non-goals
v0.8.0 does not add cloud sync, accounts-as-storage, team collaboration, remote connectors, or institutional governance. Those remain separate architectural concerns.
