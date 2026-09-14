# Sustainable Catalyst Workspace Backend v2.10.0

Workspace v2.9.0 adds policy-governed controlled runtime handoffs above the v2.7 reproduction execution plane.

## Added through v2.10.0
- revisioned execution-policy heads and immutable revisions
- immutable policy-decision receipts for reproduction execution plans
- runtime-adapter trust levels: `untrusted`, `bounded`, and `trusted`
- bounded CPU, memory, wall-time, output, PID, and temporary-storage budgets
- target-product and operation allowlists
- sandbox requirement profiles: metadata gate, adapter-attested, container-required, and remote-sandbox-required
- bounded network policies: none, server-routed-only, or allowlisted
- frozen policy, resource-budget, and sandbox envelopes propagated through server-side handoffs
- fail-closed denial of host-filesystem, Docker-socket, and privileged execution

## Enforcement boundary

Workspace is the pre-dispatch policy gate. Creating an execution plan does not execute it, and controlled handoff still requires explicit human authorization. Workspace does not accept client-supplied runtime URLs, service credentials, shell commands, or unrestricted code. Strict CPU/memory/process/container enforcement remains the responsibility of the selected specialist runtime or sandbox adapter, which must satisfy the frozen policy requirements before dispatch.

## Compatibility
- previous release: v2.7.0
- rollback release: v2.7.0
- PostgreSQL migration: `008_execution_policy_resource_budgets_sandboxing.sql`
- host API binding remains `127.0.0.1:8094`


## v2.9.0 runtime enforcement telemetry

Runtime handoffs can now receive immutable post-execution attestations through a dedicated server-to-server attestation credential. The attestation freezes observed resource usage, budget accounting, sandbox evidence, the policy-decision fingerprint, job/run identity, and a SHA-256 attestation fingerprint. Browser/WordPress clients may read attestations but cannot submit them. Workspace still does not provide unrestricted arbitrary-code execution.


## v2.10.0 runtime trust and compliance
Revisioned trust policies verify immutable v2.9 runtime attestations for bounded downstream scopes. Human waivers are explicit evidence-layer exceptions only; they never authorize execution or rewrite the original attestation.
