# Workspace v2.8.0 — Execution Policy, Resource Budgets & Runtime Sandboxing

## Purpose
v2.8.0 makes controlled runtime handoffs policy-aware and resource-bounded. It introduces revisioned execution policies and immutable eligibility decisions without moving specialist compute into Workspace.

## Policy lifecycle
1. Store a policy through `/v1/execution-policies`.
2. Policy revisions receive deterministic SHA-256 fingerprints.
3. A reproduction execution plan must reference a policy revision and a requested resource budget.
4. Workspace evaluates target, operation, adapter trust, resources, sandbox mode, network mode, and hard prohibitions.
5. The eligibility decision is frozen into the execution-plan envelope.
6. Human-authorized handoff revalidates the immutable decision before creating a durable job.
7. The policy, budget, and sandbox envelope accompany server-side compute handoffs.

## Resource budget fields
- `cpuCores`
- `memoryMb`
- `wallSeconds`
- `outputBytes`
- `pids`
- `tempStorageMb`

Requested values must not exceed the policy revision's limits.

## Runtime trust
Runtime adapters are classified as `untrusted`, `bounded`, or `trusted`. A policy can require a minimum trust level. Trust is revisioned with the adapter descriptor and therefore included in its fingerprint.

## Sandbox modes
- `metadata-gate`: Workspace performs policy gating only; intended for bounded built-in Workspace operations.
- `adapter-attested`: adapter configuration must attest a sandbox.
- `container-required`: adapter type must be a container runtime.
- `remote-sandbox-required`: adapter must be a remote-service runtime with sandbox attestation.

## Network modes
- `none`: only in-process Workspace operations are eligible.
- `server-routed-only`: in-process or server-configured routes are eligible; browser/client routes are not.
- `allowlisted`: adapter configuration must expose a server-side network allowlist.

## Hard boundaries
Execution policies cannot enable host filesystem access, Docker-socket access, or privileged execution. `noNewPrivileges` and dropped capabilities are required policy assertions. Client-supplied runtime URLs and credentials remain disallowed.

## Important scope boundary
v2.8.0 defines and enforces the **pre-dispatch eligibility and sandbox requirement contract**. For specialist services and strict container/remote sandbox modes, actual OS/container enforcement belongs to the selected runtime service. Workspace does not run arbitrary shell commands.
