# Workspace v3.3.0 install and test

1. Promote the repository with `PUSH_WORKSPACE_V3300_FINAL.sh`.
2. Deploy the backend before WordPress.
3. Verify `/health`, `/v1/platform-core-runtime/readiness`, `/v1/research-context`, and `/v1/research-bindings`.
4. Confirm migration 034 and INSERT privilege on `workspace_research_session_object_bindings`.
5. Install the v3.3.0 WordPress plugin only after backend validation passes.
