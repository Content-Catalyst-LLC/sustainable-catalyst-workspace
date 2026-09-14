# Deploy Workspace Backend v2.8.0

Use `scripts/deploy_workspace_backend_v2_8_0_vps.sh` with the v2.8 backend ZIP. The installer inherits the prior `.env`, applies migrations 002 through 008, verifies policy-table privileges, replaces the API and worker containers, and performs a policy/sandbox smoke test.

The smoke test proves:
- API and worker version 2.8.0
- execution-policy registry and revisioning
- bounded runtime-adapter trust
- blocked over-budget execution planning
- ready bounded execution planning under the same policy
- explicit human-authorized handoff
- policy decision fingerprint retained in the handoff receipt
- exact reproduction verification after the controlled job completes

Strict OS-level resource isolation remains the responsibility of an adapter/runtime that advertises and satisfies the selected sandbox mode. The Workspace process does not become an arbitrary shell executor.
