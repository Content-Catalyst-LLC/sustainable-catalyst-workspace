# Workspace v2.9.0 — Runtime Enforcement Telemetry, Budget Accounting & Execution Attestations

Workspace v2.9.0 closes the post-dispatch evidence gap introduced by controlled runtime handoffs. Each terminal runtime handoff can now receive one immutable server-to-server execution attestation tied to the frozen execution plan, policy decision, run, job, and handoff receipt.

## Added
- Runtime-execution attestation registry and immutable SHA-256 receipts.
- Dedicated runtime-attestation credential separate from the ordinary Workspace service token.
- Observed CPU core-seconds, peak memory, wall time, output bytes, PID peak, and temporary-storage peak.
- Deterministic resource-budget accounting with utilization and headroom.
- Runtime sandbox attestation comparison against the frozen v2.8 policy decision.
- Classifications: `compliant`, `budget-exceeded`, `sandbox-deviation`, `incomplete`, and `execution-failed`.
- Read-only WordPress proxy routes for attestation discovery. Browser/WordPress submission is intentionally unavailable.

## Safety boundary
Workspace still performs no unrestricted arbitrary-code execution. A runtime attestation is evidence about a completed controlled handoff; it does not grant execution authority and cannot relax the frozen execution policy.
