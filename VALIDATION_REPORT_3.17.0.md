# Workspace v3.17.0 Validation Report

## Release

**Workspace v3.17.0 — Uncertainty, Sensitivity & Probabilistic Investigation Workspace**

## Final results

- Workspace version: **3.17.0**
- Baseline: **3.16.0**
- Migration: **048**
- Typed endpoints: **254**
- New v3.17 endpoints: **18**
- Missing OpenAPI operations: **0**
- v3.17 focused tests: **7/7 PASS**
- v3.16 immediate-parent tests: **7/7 PASS**
- Combined current/parent gate: **14/14 PASS**
- Python compilation: **PASS**
- Typed client generation/check: **PASS**
- PHP syntax: **PASS**
- JavaScript syntax: **PASS**
- Full v3.16 repository → v3.17 clean-room overlay: **PASS**
- v3.16 backend → v3.17 backend-only overlay: **PASS**
- WordPress stable package identity: **PASS**
- Rollback baseline: **3.16.0**
- Catalyst Analytics R 2.2 preservation contract: **preserved by deployment gate**

## Epistemic / research boundaries

The v3.17 profile keeps all of the following false:

- `automaticProbabilityAsTruth`
- `automaticDistributionInference`
- `automaticSensitivityExecution`
- `automaticEvidenceRanking`
- `automaticTruthDetermination`
- `automaticCausalityInference`
- `automaticCulpabilityInference`
- `automaticNarrativeSelection`

Uncertain inputs remain explicit researcher-authored objects. Evidence references used as the basis for an uncertain parameter are fingerprint-pinned, and probabilistic result bindings require result fingerprints.

## Clean-room scope

The full overlay was replayed against the actual `sustainable-catalyst-workspace-v3.16.0-repository.zip`. The backend-only overlay was replayed against the actual `sustainable-catalyst-workspace-backend-v3.16.0.zip`. Both paths passed the same v3.17 validator and the combined v3.17/v3.16 focused test gate.

Expected Pydantic warnings about request-model fields named `schema` remain warnings only and did not cause test failures.

`FINAL_V31700_RELEASE_VALIDATION=PASS`
