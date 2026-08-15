# Workspace v1.5.0 — Lab & Scientific Workspace Integration

v1.5.0 makes the existing Lab handoff a governed scientific round trip.

## Added
- explicit multi-object scientific context selection for source, evidence, dataset, analysis, document, and export objects;
- workflow routing for Model Studio, Graph Studio, experiments, Bayesian inference, posterior diagnostics/predictive modeling, data transformation, and scientific visualization;
- portable `sc-workspace-lab-scientific-context/1.0` packages;
- typed `sc-workspace-lab-scientific-return/1.0` packages and `sc-workspace-scientific-artifact/1.0` artifacts;
- deterministic materialization into existing Workspace object types;
- preservation of methodology, parameters, units, uncertainty, diagnostics, and environment notes in returned artifact content;
- explicit `derived-from` traceability edges from the selected outbound context to returned Lab artifacts.

## Boundaries
Lab remains the execution environment. Workspace never automatically uploads context, starts a Lab computation, commits unmatched returns, infers scientific relationships, invokes AI, or mutates canonical Lab records. Project/handoff identity must match a local handoff before a scientific return is committed.

Storage 35, Project `sc-workspace-project/20.0`, and Export `sc-workspace-project-export/20.0` remain frozen.
