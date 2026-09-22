# Workspace v3.4.0 Install and Test

1. Promote the repository ZIP with `PUSH_WORKSPACE_V3400_FINAL.sh`.
2. Copy the backend ZIP and deploy script to the VPS.
3. Run the backend deploy script and require its final PASS.
4. Verify `/health` reports version `3.4.0`, migration lineage `035_scientific_execution_provenance_workspace.sql`, and `scientificExecutionProvenanceWorkspace=true`.
5. Only after backend success, install the v3.4.0 WordPress plugin ZIP.
6. Keep the Sustainable Catalyst shortcode registry MU guard enabled.
