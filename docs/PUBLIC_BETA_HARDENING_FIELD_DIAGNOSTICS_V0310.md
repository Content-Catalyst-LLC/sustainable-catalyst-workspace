# Public Beta Hardening & Field Diagnostics — v0.31.0

v0.31.0 hardens the Sustainable Catalyst Workspace public beta before the Research Notebook build begins.

## Field Diagnostics

The Storage & Identity drawer now includes a local Field Diagnostics surface. It can inspect browser capability, local-storage write latency, workspace serialized size, parse/serialization latency, rendered DOM density, last-known-good recovery availability, and a coarse deployment profile.

These checks are descriptive. Advisory thresholds can produce explicit attention labels, but Workspace does not calculate a hidden health, productivity, reliability, or readiness score.

## Field reports

Users can explicitly export a structured issue report containing issue type, impact, observed behavior, expected behavior, reproduction steps, and the privacy-minimized field diagnostic. A plain-text support summary can also be exported.

No report is submitted automatically. Workspace does not automatically attach project content, object text, source URLs, device identity, query strings, or URL fragments. Text entered by the user is included because it is the report itself.

## Recovery and performance

The release verifies the existing last-known-good recovery boundary and exposes non-content measurements that can help diagnose storage or interface degradation in real deployments. Advisory thresholds are currently 4 MB serialized Workspace size, 100 ms storage probe latency, 150 ms parse/serialization latency, and 6,000 rendered Workspace DOM elements.

## Data boundary

- Storage schema remains 27.
- Project schema remains `sc-workspace-project/12.0`.
- Guest use remains first-class.
- Account backup and cross-device sync remain explicit.
- No background telemetry is added.
- No automatic issue submission is added.
- No automatic repair channel is added.
