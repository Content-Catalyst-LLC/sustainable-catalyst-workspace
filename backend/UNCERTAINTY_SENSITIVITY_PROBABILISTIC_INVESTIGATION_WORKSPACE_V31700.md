# Workspace v3.17.0 — Uncertainty, Sensitivity & Probabilistic Investigation Workspace

## Purpose

v3.17.0 adds a governed uncertainty layer to Workspace so investigators and researchers can represent uncertain inputs, explicit distribution assumptions, scenario ensembles, sensitivity-analysis requests, and returned probabilistic results without confusing model output with factual truth.

Workspace remains the research orchestration and provenance authority. Workbench, Research Lab, Catalyst Analytics R, and Platform Core remain specialist execution/analysis authorities. All cross-product exchanges are reference-first and fingerprint-pinned where evidence or results are referenced.

## Durable research objects

Migration `048_uncertainty_sensitivity_probabilistic_investigation_workspace.sql` adds:

1. `UncertaintyAssessmentHead` / `workspace_uncertainty_assessment_heads`
2. `UncertaintyAssessmentRevision` / `workspace_uncertainty_assessment_revisions`
3. `UncertaintyParameter` / `workspace_uncertainty_parameters`
4. `UncertaintyScenario` / `workspace_uncertainty_scenarios`
5. `SensitivityAnalysisRequestRecord` / `workspace_sensitivity_analysis_requests`
6. `ProbabilisticResultBinding` / `workspace_probabilistic_result_bindings`
7. `UncertaintyInvestigationSnapshot` / `workspace_uncertainty_investigation_snapshots`

## Supported uncertainty methods

Assessment method families include Monte Carlo, bootstrap, Bayesian, ensemble, analytical, interval, scenario, and custom approaches. Parameter distributions include fixed, normal, lognormal, uniform, triangular, beta, gamma, Poisson, empirical, discrete, interval, and custom forms.

Sensitivity requests support Sobol, Morris, local, one-at-a-time, variance decomposition, regression, correlation, and custom methods. A request can target Workbench, Research Lab, Catalyst Analytics R, or Platform Core, but Workspace does not execute the specialist method automatically.

## Evidence and reproducibility boundaries

Uncertain parameters may cite an evidence object only when its fingerprint is also supplied. Scenarios can carry evidence references with fingerprints. Returned probabilistic results require a result fingerprint. This preserves reproducibility and prevents silent substitution of source or result objects.

A probability, interval, posterior, forecast, ensemble, or sensitivity index is treated as a model/result object—not as truth. The workspace explicitly disables automatic probability-as-truth interpretation, distribution inference, sensitivity execution, evidence ranking, truth determination, causality inference, culpability inference, and narrative selection.

## API additions

v3.17 adds 18 typed operations under `/v1/uncertainty-investigation-workspace` for the workspace profile, assessment heads/revisions, parameters, scenarios, sensitivity requests, probabilistic result bindings, project manifest/graph/diagnostics, and immutable snapshots.

## Unified Research Context

The unified project context now carries the uncertainty manifest and diagnostics and exposes counts for assessments, parameters, scenarios, sensitivity requests, probabilistic results, and unresolved uncertainty diagnostics. Canonical evidence remains in its owning Workspace/specialist object family.

## WordPress thin client

The WordPress layer remains a server-proxy thin client. v3.17 adds explicit proxy routes plus:

- `assets/js/sc-workspace-typed-client-v31700.js`
- `assets/js/sc-workspace-uncertainty-v31700.js`
- `assets/js/workspace-v3.17.0.js`
- `assets/css/workspace-v3.17.0.css`

No service credentials are exposed to the browser.
