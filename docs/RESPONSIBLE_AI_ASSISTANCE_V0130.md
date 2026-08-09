# v0.13.0 — Responsible AI Assistance

## Purpose
AI assistance must be grounded in visible Workspace context and remain subordinate to human judgment. v0.13.0 creates a project-local request/review boundary rather than embedding an opaque autonomous agent.

## Principles
- Explicit invocation only.
- Selected Workspace Objects define the grounding basis.
- No automatic remote submission.
- AI output is a draft, not evidence.
- No independent decision or publication authority.
- Human acceptance/rejection is recorded.
- Accepted output materializes as a working Document and preserves visible lineage to selected citation objects.


## Adapter boundary
Compatible Sustainable Catalyst tools can use `assets/js/sc-workspace-ai-adapter-v1.js` after the user explicitly prepares an AI request. The helper reads `sc_workspace_ai_request_v1`, constrains returned citation object IDs to the originally selected grounding objects, and returns `sc-workspace-ai-response/1.0` through `sc_workspace_ai_response_v1` or same-origin `postMessage`. Workspace accepts the response only when the local project and AI request still exist. The returned text remains a review draft until the user explicitly accepts it as a Document.
