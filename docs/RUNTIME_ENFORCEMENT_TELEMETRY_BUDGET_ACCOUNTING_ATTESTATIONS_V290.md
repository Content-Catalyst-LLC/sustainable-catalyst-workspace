# Runtime Enforcement Telemetry, Budget Accounting & Execution Attestations — v2.9.0

## Purpose
Record what a specialist runtime actually reports after a v2.8 policy-governed controlled handoff, and compare observed execution against the resource budget and sandbox requirements frozen before dispatch.

## Trust boundary
Attestation submission requires both the normal Workspace service credential and a separate `X-SC-Runtime-Attestation-Token`. WordPress exposes read-only attestation routes and never receives or forwards the runtime-attestation token.

## Immutable chain
`execution policy revision → policy decision → reproduction execution plan → human-authorized handoff receipt → terminal job/run → runtime execution attestation`.

## Budget accounting
The attestation records CPU core-seconds, peak memory, wall time, output bytes, peak PIDs, and peak temporary storage. Each reported value is compared with the frozen decision budget and receives limit, observed value, headroom, utilization percentage, and pass/fail state.

## Sandbox evidence
The attestation compares network mode, root-filesystem posture, no-new-privileges, Linux capability dropping, host-filesystem isolation, Docker-socket isolation, privileged-execution prohibition, and pinned-container requirements.
