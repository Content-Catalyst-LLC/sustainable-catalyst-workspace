# Canvas & Structured Thinking — v0.7.0

Canvas is a project-level structured-thinking contract layered over stable Workspace Objects. It is not a second artifact store.

## Data model

- Board — a bounded thinking surface with purpose and lifecycle state.
- Node — a typed proposition, entity, artifact reference, or working idea.
- Relationship — a directional typed connection between nodes.
- Frame — a named grouping of nodes used to preserve a conceptual boundary or synthesis.

Nodes may reference canonical Workspace Object IDs. Deleting an Object clears that link but does not delete the Canvas node. Deleting a Canvas node removes its relationships and frame membership.

## Synthesis

Capture synthesis materializes the active board into a canonical Document object containing nodes, relationships, and frames. This allows a visual/structured thinking state to become a portable authored artifact without changing the Canvas source.

## Privacy boundary

Catalyst Canvas handoffs carry stable project and board IDs only. Node bodies, titles, linked object content, and frame descriptions are never placed in handoff URLs.
