# Sustainable Catalyst Workspace v2.8.0

## Execution Policy, Resource Budgets & Runtime Sandboxing

Workspace v2.8.0 adds a bounded execution-policy plane above v2.7 controlled runtime handoffs.

### Added
- revisioned Execution Policy Registry in PostgreSQL
- immutable execution-policy decision receipts bound to reproduction execution plans
- explicit runtime-adapter trust levels: `untrusted`, `bounded`, `trusted`
- CPU-core, memory, wall-time, output-byte, PID, and temporary-storage budgets
- target-product and operation allowlists
- sandbox modes: `metadata-gate`, `adapter-attested`, `container-required`, `remote-sandbox-required`
- network modes: `none`, `server-routed-only`, `allowlisted`
- policy controls for read-only roots, no-new-privileges, dropped capabilities, and container pinning
- hard prohibition flags for host filesystem, Docker socket, and privileged execution
- frozen policy revision/fingerprint and policy-decision fingerprint in the execution envelope
- resource-budget and sandbox metadata propagated through server-side job handoffs
- WordPress server-proxy routes for policies and policy decisions

### Enforcement model
Creating a reproduction execution plan does not execute work. v2.8 evaluates the frozen run, adapter, target, operation, requested resources, and sandbox requirements first. A plan can become `ready` only when both the v2.7 readiness checks and the v2.8 policy decision pass. Handoff revalidates the immutable policy-decision fingerprint before queueing work.

Strict sandbox profiles are requirements on the selected runtime adapter/downstream runtime. Workspace itself does not become an unrestricted shell or arbitrary-code executor.

### Security boundaries retained
- human authorization remains required for controlled runtime handoff
- client-supplied runtime URLs remain prohibited
- client-supplied service credentials remain prohibited
- arbitrary command execution remains prohibited
- privileged execution, host-filesystem access, and Docker-socket access are not permitted by execution policies
- secret environment values are not captured

### Compatibility
- previous release: v2.7.0
- rollback release: v2.7.0
- storage schema remains 35
- project schema remains `sc-workspace-project/20.0`
- export schema remains `sc-workspace-project-export/20.0`
- migration 008 is additive
