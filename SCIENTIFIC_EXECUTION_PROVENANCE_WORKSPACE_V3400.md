# Workspace v3.4.0 — Scientific Execution & Provenance Workspace

The v3.4 provenance surface treats an execution run as a reproducible research object rather than a transient job. For each run it projects pinned inputs (datasets, model, parameter set, execution environment, runtime adapter), outputs, events, runtime receipts, and the optional Platform Core v3 research-session binding.

The provenance graph uses explicit relations such as `consumed-by`, `used-by`, `parameterized`, `executed-in`, `executed-via`, `produced`, `evidenced-by`, and `bound-to`. The graph is descriptive: it records declared and persisted lineage; it does not infer causality, scientific validity, or evidentiary weight.

Immutable snapshots can capture either one run or the project execution-provenance view. Every snapshot stores a SHA-256 provenance fingerprint and remains Workspace-owned.
