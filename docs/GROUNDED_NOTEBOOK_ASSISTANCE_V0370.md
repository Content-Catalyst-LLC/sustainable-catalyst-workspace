# Workspace v0.37.0 — Grounded Notebook Assistance

## Purpose

v0.37.0 adds a bounded assistance layer to Research Notebook. A question is prepared only against material the user deliberately selects. That selection becomes the citation universe for the answer, making grounding inspectable rather than implicit.

## Grounding model

A grounded question stores the user's question plus an ordered set of notebook-block and Workspace-object references. Each selected item receives a stable number. The request packet includes a compact representation of that material and recorded citation/source context.

Assistant responses use numbered markers such as `[1]` and `[2]`. Workspace validates every marker against the prepared selection. A response with no valid citation markers, or a marker that refers to material outside the selection, is rejected rather than saved as a grounded answer.

## Provider-neutral workflow

Workspace itself does not configure or automatically call an AI provider. A grounded request can be copied as a prompt, exported as JSON, or handed to a compatible same-origin Sustainable Catalyst assistance surface. The companion Notebook Assistance adapter provides a constrained response-return contract.

This keeps the research boundary independent from any particular model or provider while retaining a structured path for assisted research.

## Reviewable drafts

A successfully returned response is stored as a reviewable assistance draft. The user can inspect the question, grounding set, citations, response text, and status before marking it reviewed or taking any downstream action.

An assistance draft is not Evidence, Analysis, Decision, or another canonical research object merely because an assistant produced it.

## Document materialization

The user may explicitly create a standard Workspace Document from an accepted assistance draft. Materialization creates a derivative Document and leaves the assistance record and original grounding material intact.

## Request and response portability

v0.37.0 adds:

- `sc-workspace-notebook-assistance/1.0`
- `sc-workspace-notebook-assistance-request-export/1.0`
- `sc-workspace-notebook-assistance-response-export/1.0`

These records preserve the question, selected references, numbered grounding entries, citation policy, response citations, review status, and project relationship needed for portable review.

## Schemas and migration

- Workspace storage schema: 32 → 33
- Project schema: 17.0 → 18.0
- Project export schema: 17.0 → 18.0
- Notebook Workspace schema: 5.0 → 6.0
- Notebook schema: remains 3.0
- Notebook block schema: remains 3.0
- Notebook export schema: 5.0 → 6.0
- Notebook Assistance schema: 1.0
- Assistance Request Export schema: 1.0
- Assistance Response Export schema: 1.0

The migration preserves v0.36 synthesis records, v0.35 promotions, v0.34 collections and links, v0.33 source capture, existing notebooks, canonical Workspace objects, and recovery/governance state.

## Governance boundaries

v0.37.0 does not introduce automatic grounding selection, automatic AI submission, automatic answer acceptance, citation guessing, citation expansion beyond the selected set, automatic source mutation, automatic evidence creation, automatic document materialization, hidden confidence scoring, remote source fetching, or automatic publication.

## Foundation for v0.38.0

Grounded assistance completes the core research loop before **v0.38.0 — Portable & Synced Notebooks**, where notebook export/import, account backup, cross-device synchronization, restore points, and conflict-safe history are applied directly to the research environment.
