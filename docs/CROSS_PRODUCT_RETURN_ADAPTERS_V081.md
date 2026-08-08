# Sustainable Catalyst Workspace v0.8.1 — Cross-Product Return Adapters

v0.8.1 operationalizes the v0.8.0 handoff-return boundary without introducing cloud storage or a server-side broker.

## Producer helper

The WordPress plugin ships `assets/js/sc-workspace-return-adapter-v1.js`. Compatible Sustainable Catalyst tools can enqueue this helper and call `SCWorkspaceToolReturnAdapter.submit({ destination, artifacts })`. The helper reads the existing `sc_workspace_handoff_v2` session context, writes an adapter packet to `sc_workspace_handoff_return_v1`, optionally posts the same packet to an open same-origin Workspace window, and can redirect to the recorded Workspace return URL.

## Adapter envelope

`sc-workspace-return-adapter/1.0` is normalized into the existing canonical `sc-workspace-handoff-return/1.0` contract. Workspace accepts canonical packets unchanged, while the adapter envelope also recognizes common producer fields such as `source`, `tool`, `outputs`, `results`, and a single `artifact`.

## Automatic-return safety

Automatic session/postMessage returns must match an active local Project, a recorded local handoff ID, and the originating destination. Same-origin `postMessage` is enforced. Manual JSON import remains the explicit recovery/interoperability path and may create an unmatched handoff record.

## Privacy boundary

URLs still carry IDs and intent only. Returned content is transported locally in the browser session or explicitly by JSON import. No cloud synchronization, server project storage, or server handoff broker is added in this release.
