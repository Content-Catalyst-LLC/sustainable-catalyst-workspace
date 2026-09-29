# Workspace v3.39.0.1 — Neural-Symbolic Artifact Persistence Repair

Repair release for v3.39.0. The neural-symbolic compute runtime remains v3.39.0 with 101 bounded operations. This release corrects the Workspace worker persistence path so governed neural-symbolic artifacts use `sc-workspace-artifact-store/1.0` with an explicit artifact ID, Base64 JSON content, revision control, and metadata.

No database migration. No new neural operations. Rollback baseline: v3.39.0.
