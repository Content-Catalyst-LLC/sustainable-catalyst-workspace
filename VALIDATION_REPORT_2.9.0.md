# Workspace v2.9.0 Validation Report

Release: **Runtime Enforcement Telemetry, Budget Accounting & Execution Attestations**

## Release-specific gate
- Structural validator: PASS
- Backend + v2.9 targeted tests: **35 passed**
- PHP syntax: **31/31 files passed**
- Python compilation: PASS
- VPS deployment script shell syntax: PASS
- Release ZIP integrity: validated after packaging

## Historical suite
- **1,165 passed**
- **124 failed**

The historical failures are stale current-release assertions from older release contracts (for example old plugin versions, asset names, release-stage markers, README headings, or predecessor identities). No v2.9 runtime-enforcement telemetry or attestation test fails in the release-specific gate.

## v2.9 safety and provenance assertions
- Runtime attestation submission requires the normal service credential plus a separate runtime-attestation token.
- WordPress/browser routes are read-only for runtime attestations.
- A handoff must already be terminal before attestation.
- One immutable attestation is retained per runtime-handoff receipt.
- The attestation binds the handoff, job/run, and exact execution-policy decision fingerprint.
- Missing runtime metrics classify as `incomplete`, not as a false budget overage.
- Observed overages classify as `budget-exceeded`.
- Sandbox mismatches classify as `sandbox-deviation`.
- An attestation cannot relax policy, authorize a new execution, or enable arbitrary code execution.
