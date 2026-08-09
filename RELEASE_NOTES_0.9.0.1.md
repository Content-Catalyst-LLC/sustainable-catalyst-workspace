# Sustainable Catalyst Workspace v0.9.0.1

## Closing CTA Cleanup & Action Alignment

This micro-release removes the redundant closing **Open Workspace** action from the public Workspace editorial shell. The user is already inside Workspace at that point in the page, so the control did not advance the workflow.

### Changes

- Replaces the closing **Open Workspace** link with **New Project**.
- Wires the closing **New Project** action to the existing project-creation flow.
- Scrolls the opened project form into view and preserves the existing title-field focus behavior.
- Respects `prefers-reduced-motion` when scrolling.
- Retains **Explore the Library** as the secondary closing action using `/knowledge-libraries/`.
- Preserves the hero **Open Workspace** and application-intro **Go to projects** actions because those still perform meaningful navigation into the application.

### Data boundary

No storage or project migration occurs. Storage remains schema 10; projects remain `sc-workspace-project/8.0`; traceability remains `sc-workspace-traceability/1.0`.
