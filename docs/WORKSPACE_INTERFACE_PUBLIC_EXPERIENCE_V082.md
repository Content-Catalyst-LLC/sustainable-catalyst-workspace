# Workspace v0.8.2 — Interface Refinement & Public Experience

v0.8.2 is intentionally a presentation and usability release. It does not change the Workspace storage, project, object, research, analysis, decision, canvas, handoff, return, or identity schemas introduced through v0.8.1.

## Public experience

The dedicated Workspace page now uses a light institutional presentation with a restrained hero, compact Research → Evidence → Analysis → Decision → Canvas workflow rail, and three concise public principles. The large dark marketing/application slab from v0.8.1 is removed.

## Application hierarchy

The application shell uses a light research-desk treatment. Storage and identity information is progressively disclosed. Handoff diagnostics and connected-tool return history are moved behind a secondary Connections & returns disclosure.

When a project is active, Overview, Research, Analysis, Decisions, Canvas, and Objects are presented as explicit project modes. This reduces the long vertical stack while retaining the existing underlying components and data contracts.

## Navigation naming

The visitor-facing product name is Workspace. The canonical route remains `/platform/` to avoid unnecessary route churn. Tools → Workspace Page includes an explicit administrator action that relabels only matching WordPress navigation items titled `Platform` that point to the root Platform page or `/platform/`. A rollback snapshot is retained.

## Persistence boundary

Projects remain device-local. Sign-in remains optional and does not upload, claim, or synchronize project content. No cloud sync, server project storage, or server handoff broker is introduced.
