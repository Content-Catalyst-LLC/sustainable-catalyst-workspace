# Deploy Workspace backend v3.22.0

Rollback baseline: backend v3.21.0. No database migration is required.

The deployer builds and switches the neural runtime, Workspace backend, and worker, then validates backend health, direct neural health, a real bounded linear-training job submitted through Workspace, runtime registry/OpenAPI coherence, and container hardening.
