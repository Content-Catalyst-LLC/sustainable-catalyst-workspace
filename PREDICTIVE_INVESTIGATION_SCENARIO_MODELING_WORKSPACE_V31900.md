# Workspace v3.19.0 — Predictive Investigation & Scenario Modeling Workspace

Workspace v3.19.0 extends the investigative research stack with a backend-authoritative, reference-first predictive layer. It lets researchers define explicit future or counterfactual scenarios, bind fingerprinted models and data, request specialist forecasts, preserve calibration/backtest evidence, compare scenarios, and snapshot the resulting predictive research state.

## Architecture

Workspace owns scenario definitions, bindings, handoff provenance, returned-result references, comparisons, diagnostics, and snapshots. Workbench, Research Lab, Catalyst Analytics R, and Platform Core remain specialist execution/analysis authorities. Canonical investigative evidence remains in its original Workspace/Core object systems.

## Durable objects

- `PredictiveScenarioHead` / `PredictiveScenarioRevision`
- `PredictiveModelBinding`
- `PredictiveForecastRequest`
- `PredictiveForecastResultBinding`
- `PredictiveScenarioComparison`
- `PredictiveInvestigationSnapshot`

Migration: `050_predictive_investigation_scenario_modeling_workspace.sql`.

## Predictive semantics

Scenarios must carry explicit assumptions and can reference fingerprint-pinned evidence, causal questions, and uncertainty assessments. Model bindings pin model and optional environment fingerprints. Forecast requests preserve forecast kind, target, horizon, specialist destination, configuration, calibration plan, and backtest plan. Returned result bindings remain explicitly model-conditional.

Supported model families include time-series, regression, Bayesian, state-space, survival, machine-learning, simulation, ensemble, causal-forecast, and custom. Supported specialist destinations are Workbench, Research Lab, Catalyst Analytics R, and Platform Core.

## Human/epistemic boundaries

The workspace does not automatically execute forecasts, choose scenarios, select models, retrain models, convert probabilities or forecasts into truth, rank evidence, infer causality or culpability, or select a narrative. Forecasts remain conditional on data, model, assumptions, horizon, and configuration.

## API

v3.19.0 adds 18 typed endpoints, taking the contract from 272 to 290 endpoints. These cover scenario CRUD/revisions, model bindings, forecast requests, returned results, scenario comparisons, manifest/graph/diagnostics, and snapshots.
