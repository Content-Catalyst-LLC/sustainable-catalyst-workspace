# Workspace v3.18.0 — Causal Analysis & Alternative Explanation Workspace

## Purpose

v3.18.0 adds a governed causal-reasoning workspace for framing causal questions, representing researcher-authored causal structures, preserving alternative explanations, documenting identification assumptions, packaging specialist causal-analysis handoffs, and binding returned results without converting statistical/model output into truth claims.

Workspace remains the investigation orchestration and provenance authority. Workbench, Research Lab, Catalyst Analytics R, and Platform Core remain specialist analysis/execution authorities. Canonical evidence remains with its owning Workspace object family and is referenced rather than duplicated.

## Durable research objects

Migration `049_causal_analysis_alternative_explanation_workspace.sql` adds:

1. `CausalQuestionHead` / `workspace_causal_question_heads`
2. `CausalQuestionRevision` / `workspace_causal_question_revisions`
3. `CausalStructureRecord` / `workspace_causal_structures`
4. `AlternativeExplanationRecord` / `workspace_alternative_explanations`
5. `CausalIdentificationAssumption` / `workspace_causal_identification_assumptions`
6. `CausalAnalysisHandoff` / `workspace_causal_analysis_handoffs`
7. `CausalResultBinding` / `workspace_causal_result_bindings`
8. `CausalInvestigationSnapshot` / `workspace_causal_investigation_snapshots`

## Causal structures

A causal structure contains explicit variables, variable roles, and human-authored directed relations. Variable roles include exposure, outcome, confounder, mediator, collider, instrument, effect modifier, selection variable, context, latent, and other. DAG and partial-DAG structures reject directed cycles; broader causal-graph and structural-model forms may represent other researcher-defined structures.

External graph references must be fingerprint-pinned. The workspace does not silently generate or modify graph topology.

## Alternative explanations

Alternative explanations are first-class records rather than discarded branches. They can reference existing investigation hypotheses and evidence objects. Referenced hypothesis/evidence objects require fingerprints so the explanation is reproducible against the exact research state considered by the investigator.

No automatic explanation ranking or preferred explanation selection occurs.

## Identification assumptions

The workspace records explicit assumptions such as temporal order, exchangeability, positivity, consistency, no interference, no unmeasured confounding, exclusion restriction, relevance, monotonicity, parallel trends, continuity, SUTVA, measurement validity, model specification, transportability, or custom assumptions.

An assumption can be asserted, supported, challenged, violated, or unknown. Diagnostics surface challenged/violated/unknown assumptions for researcher review but never auto-resolve them.

## Causal-analysis handoffs

A causal question can be packaged for a specialist analysis using methods such as difference-in-differences, instrumental variables, matching, weighting, regression discontinuity, interrupted time series, g-formula, targeted learning, Bayesian causal analysis, structural equation modeling, negative controls, or a custom method.

The handoff records the estimand, treatment/exposure reference, outcome reference, adjustment set, configuration, destination product, and reproducibility fingerprint. Workspace does not automatically execute the method.

## Causal result bindings

Returned effect estimates, intervals, falsification tests, placebo tests, balance diagnostics, robustness checks, sensitivity diagnostics, causal graphs, and identification diagnostics are bound by reference and required result fingerprint. Results remain model- and assumption-conditional and do not become automatic statements of factual causality.

## Diagnostics

Project diagnostics flag incomplete research structure such as causal questions without structures, alternative explanations, identification assumptions, specialist handoffs, or results. They can also flag structures without explicit exposure/outcome roles, challenged/violated/unknown assumptions, handoffs without returned results, and causal results without falsification/robustness/sensitivity diagnostic bindings.

Diagnostics are descriptive only.

## API additions

v3.18 adds 18 typed operations under `/v1/causal-analysis-workspace` for profile, causal questions/revisions, causal structures, alternative explanations, identification assumptions, analysis handoffs, result bindings, combined project analysis, and immutable snapshots.

## Unified Research Context

The unified project context now carries the combined causal investigation analysis and exposes counts for causal questions, structures, alternative explanations, identification assumptions, analysis handoffs, result bindings, and unresolved diagnostics.

## WordPress thin client

The WordPress layer remains a server-proxy thin client. v3.18 adds explicit proxy routes plus:

- `assets/js/sc-workspace-typed-client-v31800.js`
- `assets/js/sc-workspace-causal-analysis-v31800.js`
- `assets/js/workspace-v3.18.0.js`
- `assets/css/workspace-v3.18.0.css`

No service credentials are exposed to the browser.
