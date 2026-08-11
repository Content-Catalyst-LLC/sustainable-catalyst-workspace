# Public Product Beta III — v0.70.0

## Purpose

v0.70.0 validates Workspace as one coherent product journey rather than a collection of independent subsystems. The explicit journey is:

**Discover → Capture → Organize → Analyze → Synthesize → Decide → Compose → Review → Export / Handoff**

## Product-journey surface

The Start area includes a Product Journey route. It performs a local topology check for the route and primary action required at each stage, then supports a manual walkthrough. Manual walkthrough marks live in `sessionStorage` only and are not project data.

## Governance

- No hidden readiness, productivity, or completion score.
- No behavioral telemetry or automatic submission.
- No automatic project mutation or lifecycle advancement.
- No inferred claim that a user completed a stage merely because a route exists.
- Journey exports contain topology/manual-review state only; no project content, object text, source URLs, query strings, raw user agent, or device identifier.
- The Knowledge Library remains the public discovery entry; Workspace remains the local-first working environment; specialized Lab tools remain deliberate handoffs.

## Schema boundary

Storage remains 35. Project remains `sc-workspace-project/20.0`. Project Export remains `sc-workspace-project-export/20.0`. No migration is required.
