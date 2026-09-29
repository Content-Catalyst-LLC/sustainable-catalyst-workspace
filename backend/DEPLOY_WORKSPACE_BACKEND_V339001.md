# Deploy Workspace Backend v3.39.0.1

Requires `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.39.0`. The neural runtime remains v3.39.0 / 101 bounded operations. The deployment builds backend, worker, and neural images; runs the persistence regression before switch; switches to v3.39.0.1; then submits a real neural-symbolic inference job and requires success.
